from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
from mechanician_openai import OpenAIChatConnector
from mechanician import TAGAI
from typing import Dict
from abc import ABC, abstractmethod
import json
import asyncio

load_dotenv()

###############################################################################
## AIInstanceFactory and BasicOpenAIInstanceFactory classes
###############################################################################
 
class AIInstanceFactory(ABC):
    @abstractmethod
    def create_ai_instance():
        pass


class BasicOpenAIInstanceFactory(AIInstanceFactory):

    def __init__(self, api_key, model_name, ai_tools=[]):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name or os.getenv("OPENAI_MODEL_NAME")


    def create_ai_instance(self):
        ai_connector = OpenAIChatConnector(api_key=self.api_key, model_name=self.model_name)
        ai = TAGAI(ai_connector=ai_connector, name="Daring Mechanician AI")
        return ai


###############################################################################
## MechanicianWebApp class
###############################################################################
 
class MechanicianWebApp:

    def __init__(self, ai_factory: 'AIInstanceFactory', prompt_tools=[]):
        # Initialize class variables
        self.ai_factory = ai_factory
        self.app = FastAPI()
        # self.app.mount("/static", StaticFiles(directory="./templates"), name="static")
        self.templates = Jinja2Templates(directory="./templates")
        self.ai_instances: Dict[str, TAGAI] = {}

        # Setup routes and WebSocket events
        self.setup_routes()
        self.setup_websocket_events()


    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
    

    def setup_routes(self):
        @self.app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            return self.templates.TemplateResponse("index.html", {"request": request})


    def setup_websocket_events(self):

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            print("websocket accept")
            try:
                while True:
                    data = await websocket.receive_text()
                    sid = websocket.client
                    ai_instance = self.get_ai_instance(sid)
                    input_text = json.loads(data).get("data", "")  # Adjust according to the expected format
                    # print(f"input_text: {input_text}")
                    try:
                        for chunk in ai_instance.ai_connector.get_stream(input_text):
                            if hasattr(chunk, 'choices') and chunk.choices:
                                content = chunk.choices[0].delta.content
                                if content:
                                    # print(content)
                                    await websocket.send_text(content)
                                    await asyncio.sleep(0)
                    except Exception as e:
                        print(f"Error processing AI response: {e}")
                        await websocket.send_text(f"Error: {e}")
                        break
            except WebSocketDisconnect:
                print("Client disconnected")
                # Perform any cleanup or resource release here


    def get_ai_instance(self, sid) -> OpenAIChatConnector:
        if sid not in self.ai_instances:
            self.ai_instances[sid] = self.ai_factory.create_ai_instance()
        return self.ai_instances[sid]


###############################################################################
## Main application initialization
###############################################################################
    
# To run the application with Uvicorn, for example:
# uvicorn mechanician_ui.app:app --reload
def init_app():
    ai_factory = BasicOpenAIInstanceFactory(api_key=os.getenv("OPENAI_API_KEY"), 
                                            model_name=os.getenv("OPENAI_MODEL_NAME"))
    return MechanicianWebApp(ai_factory)

app = init_app()

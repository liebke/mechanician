from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException, WebSocketDisconnect
from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
from mechanician_openai import OpenAIChatConnectorFactory
from mechanician.ai_connectors import AIConnectorFactory
from mechanician import TAGAI, TAGAIFactory
from typing import Dict
from abc import ABC, abstractmethod
import json
import asyncio
from pprint import pprint

from mechanician.prompting.tools import PromptTools, PromptToolKit


load_dotenv()


###############################################################################
## MechanicianWebApp class
###############################################################################
 
class MechanicianWebApp:

    def __init__(self, 
                 ai_connector_factory: 'AIConnectorFactory',
                 prompt_tools=[],
                 ai_instructions=None, 
                 tool_instructions=None,
                 instruction_set_directory=None,
                 tool_instruction_file_name="tool_instructions.json",
                 ai_instruction_file_name="ai_instructions.md",
                 ai_tools=None, 
                 name="Daring Mechanician AI",
                 template_directory="./templates"):
        
        # Initialize class variables
        self.ai_connector_factory = ai_connector_factory
        self.prompt_tools = prompt_tools
        self.ai_instructions = ai_instructions
        self.tool_instructions = tool_instructions
        self.instruction_set_directory = instruction_set_directory
        self.tool_instruction_file_name = tool_instruction_file_name
        self.ai_instruction_file_name = ai_instruction_file_name
        self.ai_tools = ai_tools
        self.name = name

        self.ai_factory = TAGAIFactory(ai_connector_factory=ai_connector_factory,
                                       name = self.name,
                                       ai_tools = self.ai_tools,
                                       ai_instructions = self.ai_instructions,
                                       tool_instructions = self.tool_instructions,
                                       instruction_set_directory = self.instruction_set_directory,
                                       tool_instruction_file_name = self.tool_instruction_file_name,
                                       ai_instruction_file_name = self.ai_instruction_file_name)


        self.app = FastAPI()
        # self.app.mount("/static", StaticFiles(directory="./templates"), name="static")
        self.templates = Jinja2Templates(directory=template_directory)
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
                    processed_prompt = self.preprocess_prompt(ai_instance, input_text, prompt_tools=self.prompt_tools)
                    if processed_prompt.get("status", "noop") == "error":
                        await websocket.send_text(processed_prompt.get("prompt", ""))
                        continue
                    prompt = processed_prompt.get("prompt", '')
                    # If preprocessed prompt is None, we should skip it
                    if prompt == '':
                        continue
                            # print(f"input_text: {input_text}")
                    try:
                        for chunk in ai_instance.ai_connector.get_stream(prompt):
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


    def get_ai_instance(self, sid) -> TAGAI:
        if sid not in self.ai_instances:
            self.ai_instances[sid] = self.ai_factory.create_ai_instance()
        return self.ai_instances[sid]
    

    ###############################################################################
    ## PREPRCOESS_PROMPT
    ###############################################################################

    def preprocess_prompt(self, ai: 'TAGAI', prompt: str, prompt_tools: 'PromptTools' = None):

        # Load a file
        if prompt.startswith('/call'):
            print("Calling function...")
            print(prompt)
            parsed_prompt = prompt_tools.parse_command_line(prompt)
            if parsed_prompt is None:
                return f"Invalid /call command: {prompt}"
            print("Parsed Prompt:")
            pprint(parsed_prompt)
            tool_resp = prompt_tools.call_function(parsed_prompt.get("function_name"), parsed_prompt.get("params"))
            return tool_resp

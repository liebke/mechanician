from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, status, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mechanician.ai_connectors import AIConnectorFactory
from mechanician import TAGAI, TAGAIFactory
from typing import Dict
import json
import asyncio
from pprint import pprint
import pkg_resources
from mechanician.prompting.tools import PromptTools
import os
from mechanician_ui.auth import authenticate_user, create_access_token #, ACCESS_TOKEN_EXPIRE_MINUTES

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse
from mechanician_ui.secrets import SecretsManager, BasicSecretsManager


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
                 secrets_manager: 'SecretsManager'=None,
                 users_secrets: 'SecretsManager'=None):
        
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

        self.secrets_manager = secrets_manager or BasicSecretsManager(secrets={})
        # to get a string like this run:
        # openssl rand -hex 32
        self.secrets_manager.set_secret("SECRET_KEY", os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"))
        self.secrets_manager.set_secret("ALGORITHM", os.getenv("ALGORITHM", "HS256"))
        self.secrets_manager.set_secret("ACCESS_TOKEN_EXPIRE_MINUTES", os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

        self.users_secrets = users_secrets or BasicSecretsManager(secrets={})
        admin_username = os.getenv("ADMIN_USERNAME", "mechanician")
        print(f"admin_username: {admin_username}")
        admin_password = os.getenv("ADMIN_PASSWORD", None)
        print(f"admin_password: {admin_password}")
        if admin_password is None:
            self.users_secrets.set_secret(admin_username, {"username": admin_username, "hashed_password": None})
        else:
            admin_hashed_password = pwd_context.hash(admin_password)

        admin_user = {"username": admin_username, 
                      "hashed_password": admin_hashed_password}
        print(f"admin_user: {admin_user}")
        self.users_secrets.set_secret(admin_username, admin_user)


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
        # Get the path to the templates directory
        template_directory = pkg_resources.resource_filename('mechanician_ui', 'templates')
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
        

        @self.app.post("/token")
        async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
            print(f"form_data: {form_data.username}, {form_data.password}")
            user = authenticate_user(self.users_secrets, form_data.username, form_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            ACCESS_TOKEN_EXPIRE_MINUTES = int(self.secrets_manager.get_secret("ACCESS_TOKEN_EXPIRE_MINUTES"))
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(self.secrets_manager,
                                               data={"sub": user["username"]}, 
                                               expires_delta=access_token_expires)
            return {"access_token": access_token, "token_type": "bearer"}
        

        @self.app.get("/login")
        async def login(request: Request):
            return self.templates.TemplateResponse("login.html", {"request": request})


    def setup_websocket_events(self):

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            print("WebSocket connection accepted")
            try:
                # Wait for authentication token
                try:
                    auth_data = await asyncio.wait_for(websocket.receive_text(), timeout=30)  # Adjust timeout as needed
                    auth_data = json.loads(auth_data)
                    token = auth_data.get("token", "")
                    # Decode and validate the JWT token
                    SECRET_KEY = self.secrets_manager.get_secret("SECRET_KEY")
                    ALGORITHM = self.secrets_manager.get_secret("ALGORITHM")
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                except asyncio.TimeoutError:
                    print("Authentication timeout. Closing connection.")
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
                except (JWTError, json.JSONDecodeError) as e:
                    print(f"Invalid token. Closing connection. Error: {e}")
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
                except Exception as e:
                    print(f"Unexpected error during authentication: {e}")
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return

                # Proceed with your normal WebSocket communication
                while True:
                    try:
                        data = await websocket.receive_text()
                        sid = websocket.client
                        ai_instance = self.get_ai_instance(sid)
                        input_text = json.loads(data).get("data", "")
                        processed_prompt = self.preprocess_prompt(ai_instance, input_text, prompt_tools=self.prompt_tools)
                        if processed_prompt.get("status", "noop") == "error":
                            await websocket.send_text(json.dumps(processed_prompt))
                            continue
                        prompt = processed_prompt.get("prompt", '')
                        if prompt == '':
                            continue
                        try:
                            for chunk in ai_instance.ai_connector.get_stream(prompt):
                                if hasattr(chunk, 'choices') and chunk.choices:
                                    content = chunk.choices[0].delta.content
                                    if content:
                                        await websocket.send_text(content)
                                        await asyncio.sleep(0)
                        except Exception as e:
                            print(f"Error processing AI response: {e}")
                            await websocket.send_text(json.dumps({"error": str(e)}))
                            break
                    except WebSocketDisconnect:
                        print("Client disconnected")
                        break
            except Exception as e:
                # This outer exception block is to catch any unexpected errors outside the main while loop
                print(f"Unexpected error: {e}")



    def get_ai_instance(self, sid) -> TAGAI:
        if sid not in self.ai_instances:
            self.ai_instances[sid] = self.ai_factory.create_ai_instance()
        return self.ai_instances[sid]
    

    ###############################################################################
    ## PREPRCOESS_PROMPT
    ###############################################################################

    def preprocess_prompt(self, ai: 'TAGAI', prompt: str, prompt_tools: 'PromptTools' = None):
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
        else:
            return {"status": "noop", "prompt": prompt}
        


    

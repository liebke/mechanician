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

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from starlette.responses import Response, RedirectResponse  # Import Response for setting cookies
from mechanician_ui.secrets import SecretsManager, BasicSecretsManager
from mechanician_ui.auth import CredentialsManager, BasicCredentialsManager

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    confirm_password: str

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
                 secrets_manager: SecretsManager=None,
                 credentials_manager: CredentialsManager=None,
                 credentials_file_path="./credentials.json",
                 dm_admin_username=None,
                 dm_admin_password=None,):
        
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

        self.credentials_manager = credentials_manager or BasicCredentialsManager(secrets_manager=self.secrets_manager,
                                                                                  credentials_filename=credentials_file_path)
        dm_admin_username = dm_admin_username or os.getenv("DM_ADMIN_USERNAME", "mechanician")
        if not self.credentials_manager.user_exists(dm_admin_username):
            dm_admin_password = dm_admin_password or os.getenv("DM_ADMIN_PASSWORD", None)
            if dm_admin_password is None:
                raise ValueError("dm_admin_password must be provided or DM_ADMIN_PASSWORD environment variable must be set.")
            else:
                self.credentials_manager.add_credentials(dm_admin_username, dm_admin_password)


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
            user = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
            if user is None:
                username = ""
            else:
                username = user.get("username", "")
            print(f"Access Token: {request.cookies.get('access_token')}")
            print(f"Username: {username}")
            return self.templates.TemplateResponse("index.html", 
                                                   {"request": request,
                                                    "ai_name": self.name,
                                                    "username": username})
        

        @self.app.post("/token")
        async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
            username = form_data.username
            if not self.credentials_manager.verify_password(form_data.username, form_data.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token = self.credentials_manager.create_access_token(username, data={"sub": username})
            # Set the token in a secure HttpOnly cookie
            response.set_cookie(key="access_token", value=access_token, httponly=True, samesite='Lax')
            return {"access_token": access_token, "token_type": "bearer"}
        

        @self.app.get("/login")
        async def login(request: Request):
            return self.templates.TemplateResponse("login.html", {"request": request})
        

        @self.app.get("/create_user")
        async def login(request: Request):
            try:
                self.verify_access_token(request)
            except HTTPException as e:
                print(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            return self.templates.TemplateResponse("create_user.html", {"request": request})
        

        @self.app.post("/create_user")
        async def create_user(request: Request, user: UserCreate):
            try:
                self.verify_access_token(request)
            except HTTPException as e:
                print(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            if user.password != user.confirm_password:
                raise HTTPException(status_code=400, detail="Passwords do not match")
            
            # Add your user creation logic here
            create_status = self.credentials_manager.add_credentials(user.username, user.password)
            if not create_status:
                raise HTTPException(status_code=400, detail="User already exists")

            return {"message": "User created successfully"}
        

        @self.app.post("/logout")
        def logout():
            print("Logging out...")
            response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
            response.delete_cookie(key="access_token")
            return response

        

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
                    if self.credentials_manager.verify_access_token(token):
                        print("Token verified")
                    else:
                        print("Invalid token. Closing connection.")
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        return
                except asyncio.TimeoutError:
                    print("Authentication timeout. Closing connection.")
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


    def verify_access_token(self, request: Request):
        token = request.cookies.get("access_token")
        print(f"Token: {token}")
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            validation_response = self.credentials_manager.verify_access_token(token)
            print(f"Validation response: {validation_response}")
            if not validation_response:
                raise credentials_exception
        except Exception as e:
            raise credentials_exception


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
        


    

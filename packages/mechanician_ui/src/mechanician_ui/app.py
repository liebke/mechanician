from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, status, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mechanician.ai_connectors import AIConnectorFactory
from mechanician import TAGAI, TAGAIFactory
from typing import Dict
import json
import asyncio
from pprint import pprint
import pkg_resources
from mechanician.tools import PromptTools, MechanicianTools, PromptToolKit
import os

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import HTMLResponse
from starlette.responses import Response, RedirectResponse  # Import Response for setting cookies
from mechanician_ui.secrets import SecretsManager, BasicSecretsManager
from mechanician_ui.auth import CredentialsManager, BasicCredentialsManager

from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)



class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    confirm_password: str
    user_role: str

class UserUpdate(BaseModel):
    name: str
    username: str
    password: str
    new_password: str
    confirm_new_password: str
    user_role: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

  
###############################################################################
## MechanicianWebApp class
###############################################################################
 
class MechanicianWebApp:
    stop_generation = False

    def __init__(self, 
                 ai_connector_factory: 'AIConnectorFactory',
                 prompt_tools=None,
                 ai_instructions=None, 
                 ai_tool_instructions=None,
                 instruction_set_directory=None,
                 tool_instruction_file_name="ai_tool_instructions.json",
                 ai_instruction_file_name="ai_instructions.md",
                 ai_tools=None, 
                 name="Daring Mechanician AI",
                 secrets_manager: SecretsManager=None,
                 credentials_manager: CredentialsManager=None,
                 credentials_file_path="./credentials.json",
                 dm_admin_username=None,
                 dm_admin_password=None):
        
        # Initialize class variables
        self.ai_connector_factory = ai_connector_factory
        self.ai_instructions = ai_instructions
        self.ai_tool_instructions = ai_tool_instructions
        self.instruction_set_directory = instruction_set_directory
        self.tool_instruction_file_name = tool_instruction_file_name
        self.ai_instruction_file_name = ai_instruction_file_name
        self.ai_tools = ai_tools
        self.name = name

        if prompt_tools is not None:
            if isinstance(prompt_tools, MechanicianTools):
                self.prompt_tools = prompt_tools
            elif isinstance(prompt_tools, list):
                self.prompt_tools = PromptToolKit(tools=prompt_tools)
            else:
                raise ValueError(f"prompt_tools must be an instance of PromptTools or a list of PromptTools. Received: {prompt_tools}")


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
                admin_attrs = {"user_role": "Admin", "name": "Mechanician Admin"}
                self.credentials_manager.add_credentials(dm_admin_username, dm_admin_password, admin_attrs)

        self.client_connections = {}
        self.ai_factory = TAGAIFactory(ai_connector_factory=ai_connector_factory,
                                       name = self.name,
                                       ai_tools = self.ai_tools,
                                       ai_instructions = self.ai_instructions,
                                       ai_tool_instructions = self.ai_tool_instructions,
                                       instruction_set_directory = self.instruction_set_directory,
                                       tool_instruction_file_name = self.tool_instruction_file_name,
                                       ai_instruction_file_name = self.ai_instruction_file_name)


        self.app = FastAPI()
        # Get the path to the templates directory
        template_directory = pkg_resources.resource_filename('mechanician_ui', 'templates')
        static_files_directory = pkg_resources.resource_filename('mechanician_ui', 'static')
        self.templates = Jinja2Templates(directory=template_directory)
        self.app.mount("/static", StaticFiles(directory=static_files_directory), name="static")
        self.ai_instances: Dict[str, TAGAI] = {}
        # Setup routes and WebSocket events
        self.setup_routes()
        self.setup_websocket_events()

        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.client_websockets: Dict[str, WebSocket] = {}


    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
    

    def setup_routes(self):

        @self.app.get("/", response_class=HTMLResponse)
        async def index_get(request: Request):
            user = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
            if user is None:
                return self.templates.TemplateResponse("login.html", 
                                                       {"request": request})
            else:
                username = user.get("username", "")

            return self.templates.TemplateResponse("index.html", 
                                                   {"request": request,
                                                    "ai_name": self.name,
                                                    "username": username,
                                                    "name": user.get("name", username),})
        

        @self.app.post("/", response_class=HTMLResponse)
        async def index_post(request: Request):
            user = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
            if user is None:
                return self.templates.TemplateResponse("login.html", 
                                                       {"request": request})
            else:
                username = user.get("username", "")

            form_data = await request.form()
            form_data_dict = dict(form_data)
            prompt = form_data_dict.get("prompt", "")
            return self.templates.TemplateResponse("index.html", 
                                                   {"request": request,
                                                    "ai_name": self.name,
                                                    "username": username,
                                                    "name": user.get("name", username),
                                                    "prompt": prompt,})
        

        @self.app.post("/call_prompt_tool", response_class=HTMLResponse)
        async def call_prompt_tool(request: Request):
            user = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            form_data = await request.form()
            form_data_dict = dict(form_data)
            input_text = f"/call {form_data_dict.get('function_name')}"
            # add parameters to input_text
            for k, v in form_data_dict.items():
                if k != "function_name":
                    input_text += f' {k}="{v}"'

            ai_instance = self.get_ai_instance(request.cookies.get("access_token"))
            generated_prompt = self.preprocess_prompt(ai_instance, input_text, prompt_tools=self.prompt_tools)
            return JSONResponse(content=generated_prompt)
        


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
            return self.templates.TemplateResponse("login.html", 
                                                   {"request": request})
        

        @self.app.get("/create_user")
        async def create_user_get(request: Request):
            try:
                self.verify_access_token(request)
            except HTTPException as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            user = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
            if user is None:
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            else:
                username = user.get("username", "anonymous")
                display_name = user.get("name", username)
            
            if user.get("user_role", "User") != "Admin":
                response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            return self.templates.TemplateResponse("create_user.html",
                                                   {"request": request,
                                                    "ai_name": self.name,
                                                    "username": username,
                                                    "name": display_name})
        

        @self.app.post("/create_user")
        async def create_user_post(request: Request, user: UserCreate):
            try:
                self.verify_access_token(request)
            except HTTPException as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            user_data = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
            if user_data is None:
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            elif user_data.get("user_role", "User") != "Admin":
                response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            if user.password != user.confirm_password:
                raise HTTPException(status_code=400, detail="Passwords do not match")
            
            # Add your user creation logic here
            attrs = {"user_role": user.user_role, "name": user.name}
            create_status = self.credentials_manager.add_credentials(user.username, user.password, attrs)
            if not create_status:
                raise HTTPException(status_code=400, detail="User already exists")

            return {"message": "User created successfully"}
        


        @self.app.get("/user")
        async def user_get(request: Request):
            try:
                self.verify_access_token(request)
                user_data = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
                if user_data is None:
                    response = RedirectResponse(url='/create_user', status_code=status.HTTP_303_SEE_OTHER)
                    return response
                
                username = user_data.get("username", "")
                display_name = user_data.get("name", username)
                user_role = user_data.get("user_role", "User")

            except HTTPException as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            return self.templates.TemplateResponse("user.html", 
                                                   {"request": request,
                                                    "username": username,
                                                    "ai_name": self.name,
                                                    "name": display_name,
                                                    "user_role": user_role})
        

        @self.app.post("/user")
        async def user_post(request: Request, user: UserUpdate):
            try:
                self.verify_access_token(request)
            except HTTPException as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            if user.new_password != "":
                if user.new_password != user.confirm_new_password:
                    logger.error("Passwords do not match")
                    raise HTTPException(status_code=400, detail="Passwords do not match")
            
                update_status = self.credentials_manager.update_password(user.username, 
                                                                         user.password, 
                                                                         user.new_password)
                if not update_status:
                    logger.error("User password update error")
                    raise HTTPException(status_code=400, detail="User password update error")
                
            update_status = self.credentials_manager.update_user_attributes(user.username,
                                                                            password=user.password,
                                                                            attributes={"name": user.name})
            if not update_status:
                logger.error("User attribute update error")
                raise HTTPException(status_code=400, detail="User attribute update error")

            return {"message": "User update successfully"}
        

        @self.app.post("/logout")
        def logout():
            logger.debug("Logging out...")
            response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
            response.delete_cookie(key="access_token")
            return response
        

        @self.app.post("/new")
        def new_session(request: Request):
            logger.debug("Starting new session...")
            # get token from cookie
            token = request.cookies.get("access_token")
            # get sid from client_connections
            sid = self.client_connections.get(token, None)
            # clear ai instance
            if sid:
                self.clear_ai_instance(sid)

            response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
            return response
        

        @self.app.get("/prompt_tools")
        async def prompt_tools(request: Request):
            try:
                self.verify_access_token(request)
                user_data = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
                if user_data is None:
                    response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                    return response
                
                username = user_data.get("username", "")
                display_name = user_data.get("name", username)
                user_role = user_data.get("user_role", "User")

            except HTTPException as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response

            return self.templates.TemplateResponse("prompt_tools.html", 
                                                   {"request": request,
                                                    "prompt_tool_instructions": self.prompt_tools.get_tool_instructions(),
                                                    "username": username,
                                                    "ai_name": self.name,
                                                    "name": display_name,
                                                    "user_role": user_role})

        

    def setup_websocket_events(self):

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            logger.debug("WebSocket connection accepted")
            sid = str(websocket.client)
            try:
                # Authentication (Assuming this is a separate method for clarity)
                if not await self.authenticate_websocket(websocket):
                    logger.info("Authentication failed")
                    return
                
                # Main WebSocket communication loop
                while True:
                    await self.handle_incoming_messages(websocket)
            except WebSocketDisconnect:
                logger.info("Client disconnected")
                self.cleanup(sid)



    async def authenticate_websocket(self, websocket: WebSocket) -> bool:
        """Handle authentication for the WebSocket connection."""
        try:
            auth_data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
            auth_data = json.loads(auth_data)
            token = auth_data.get("token", "")
            sid = str(websocket.client)
            self.client_connections[token] = sid
            self.client_websockets[token] = websocket
            if self.credentials_manager.verify_access_token(token):
                logger.debug("Token verified")
                return True
            else:
                logger.info("Invalid token. Closing connection.")
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return False
        except asyncio.TimeoutError:
            logger.info("Authentication timeout. Closing connection.")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return False
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return False


    async def handle_incoming_messages(self, websocket: WebSocket):
        """Process incoming WebSocket messages."""
        async for message in websocket.iter_text():
            data = json.loads(message)
            input_type = data.get("type", "")
            if input_type == "stop":
                await self.stop_text_generation(websocket)
            else:
                await self.start_text_generation(websocket, data)


    async def start_text_generation(self, websocket: WebSocket, data: dict):
        """Starts the text generation process in a separate task."""
        sid = str(websocket.client)
        if sid in self.active_tasks:
            self.active_tasks[sid].cancel()
        self.active_tasks[sid] = asyncio.create_task(self.generate_text(websocket, data))


    async def generate_text(self, websocket: WebSocket, data: dict):
        """The actual text generation logic."""
        input_text = data.get("data", "")
        processed_prompt = self.preprocess_prompt(self.get_ai_instance(websocket), input_text, prompt_tools=self.prompt_tools)
        if processed_prompt.get("status", "noop") == "error":
            await websocket.send_text(json.dumps(processed_prompt))
            return
        prompt = processed_prompt.get("prompt", '')
        if prompt == '':
            return
        try:
            no_content = True
            while no_content:
                stream = self.get_ai_instance(websocket).ai_connector.get_stream(prompt)
                for content in self.get_ai_instance(websocket).ai_connector.process_stream(stream):
                    if self.stop_generation:
                        self.stop_generation = False
                        break

                    if content is None:
                        no_content = True
                        break
                    else:
                        no_content = False
                        await websocket.send_text(content)
                        await asyncio.sleep(0)
        except asyncio.CancelledError:
            logger.info("Text generation cancelled.")
        except Exception as e:
            logger.error(f"Error processing AI response: {e}")
            await websocket.send_text(json.dumps({"error": str(e)}))

    async def stop_text_generation(self, websocket: WebSocket):
        """Cancels the text generation task."""
        sid = str(websocket.client)
        if task := self.active_tasks.get(sid):
            task.cancel()
            logger.debug("Text generation stopped.")
            self.active_tasks.pop(sid, None)

    def cleanup(self, sid: str):
        """Clean up resources when the WebSocket connection is closed."""
        if task := self.active_tasks.get(sid):
            task.cancel()
        self.active_tasks.pop(sid, None)
        # Perform additional cleanup as necessary


    def verify_access_token(self, request: Request):
        token = request.cookies.get("access_token")
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            validation_response = self.credentials_manager.verify_access_token(token)
            logger.debug(f"Validation response: {validation_response}")
            if not validation_response:
                raise credentials_exception
        except Exception as e:
            raise credentials_exception


    def get_ai_instance(self, sid) -> TAGAI:
        if sid not in self.ai_instances:
            self.ai_instances[sid] = self.ai_factory.create_ai_instance()
        return self.ai_instances[sid]
    

    def clear_ai_instance(self, sid):
        if sid in self.ai_instances:
            del self.ai_instances[sid]
            
    

    ###############################################################################
    ## PREPRCOESS_PROMPT
    ###############################################################################

    def preprocess_prompt(self, ai: 'TAGAI', prompt: str, prompt_tools: 'PromptTools' = None):
        if prompt.startswith('/call'):
            parsed_prompt = prompt_tools.parse_command_line(prompt)
            if parsed_prompt is None:
                return f"Invalid /call command: {prompt}"
            tool_resp = prompt_tools.call_function(parsed_prompt.get("function_name"), params=parsed_prompt.get("params"))
            return tool_resp
        else:
            return {"status": "noop", "prompt": prompt}
        


    

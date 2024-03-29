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
from mechanician.tools import PromptTools, MechanicianTools, PromptToolKit, MechanicianToolsFactory
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
                 prompt_tools_factory=None,
                 ai_instructions=None, 
                 ai_tool_instructions=None,
                 instruction_set_directory=None,
                 tool_instruction_file_name="ai_tool_instructions.json",
                 ai_instruction_file_name="ai_instructions.md",
                 ai_tools_factory=None, 
                 name="Daring Mechanician AI",
                 secrets_manager: SecretsManager=None,
                 credentials_manager: CredentialsManager=None,
                 credentials_file_path="./credentials.json",
                 dm_admin_username=None,
                 dm_admin_password=None):
        
        # Initialize class variables
        self.ai_connector_factory = ai_connector_factory
        self.prompt_tools_factory = prompt_tools_factory
        self.ai_instructions = ai_instructions
        self.ai_tool_instructions = ai_tool_instructions
        self.instruction_set_directory = instruction_set_directory
        self.tool_instruction_file_name = tool_instruction_file_name
        self.ai_instruction_file_name = ai_instruction_file_name
        self.ai_tools_factory = ai_tools_factory
        self.name = name

        self.secrets_manager = secrets_manager or BasicSecretsManager(secrets={})
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

        self.ai_factory = TAGAIFactory(ai_connector_factory=ai_connector_factory,
                                       name = self.name,
                                       ai_tools_factory = self.ai_tools_factory,
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
        self.prompt_tools_instances: Dict[str, PromptTools] = {}
        # Setup routes and WebSocket events
        self.setup_routes()
        self.setup_websocket_events()

        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.sid_to_tokens: Dict[WebSocket, str] = {}
        self.token_to_sids: Dict[str, str] = {}


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
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            form_data = await request.form()
            form_data_dict = dict(form_data)
            input_text = f"/call {form_data_dict.get('function_name')}"
            # add parameters to input_text
            for k, v in form_data_dict.items():
                if k != "function_name":
                    input_text += f' {k}="{v}"'

            username = user.get("username", access_token)
            ai_instance = self.get_ai_instance(username, context=self.get_context(access_token))
            prompt_tools=self.get_prompt_tools_instance(username, context=self.get_context(access_token))
            generated_prompt = self.preprocess_prompt(ai_instance, input_text, prompt_tools)
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
            # get sid from token
            sid = self.token_to_sids.get(token, None)
            user = self.credentials_manager.get_user_by_token(token)
            username = user.get("username", token)
            # clear ai instance
            if sid:
                self.clear_ai_instance(username)

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

            token = request.cookies.get("access_token")
            prompt_tools=self.get_prompt_tools_instance(username, context=self.get_context(token))
            return self.templates.TemplateResponse("prompt_tools.html", 
                                                   {"request": request,
                                                    "prompt_tool_instructions": prompt_tools.get_tool_instructions(),
                                                    "username": username,
                                                    "ai_name": self.name,
                                                    "name": display_name,
                                                    "user_role": user_role})
        

        @self.app.get("/prompt_tools/templates/{template_name}")
        async def prompt_tools_templates(request: Request):
            try:
                self.verify_access_token(request)
                user_data = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
                if user_data is None:
                    response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                    return response

            except HTTPException as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response

            username = user_data.get("username", None)
            if username is None:
                return JSONResponse(content={"error": "No username provided."})
            
            # get prompt template name from url path
            template_name = request.path_params.get("template_name", None)
            token = request.cookies.get("access_token")
            prompt_tools=self.get_prompt_tools_instance(username, context=self.get_context(token))
            if template_name is None:
                return JSONResponse(content={"error": "No prompt template name provided."})
            else:
                prompt_template = prompt_tools.get_prompt_template(prompt_template_name=template_name)
                return JSONResponse(content=prompt_template)

        

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
            except Exception as e:
                # Identify the error type and print it
                logger.error(f"Unexpected error: {e}")
                self.cleanup(sid)



    async def authenticate_websocket(self, websocket: WebSocket) -> bool:
        """Handle authentication for the WebSocket connection."""
        try:
            auth_data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
            auth_data = json.loads(auth_data)
            token = auth_data.get("token", "")
            sid = str(websocket.client)
            self.token_to_sids[token] = sid
            self.sid_to_tokens[sid] = token
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
            self.cleanup(sid)
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


    def get_context(self, token:str):
        user = self.credentials_manager.get_user_by_token(token)
        access_token_data = self.credentials_manager.decode_access_token(token)
        return {"username": user.get("username", ""), 
                "user_role": user.get("user_role", "User"), 
                "access_token_data": access_token_data}
    

    def merge_client_message_history(self, message_history, client_message_history):
        merged_message_history = []
        if not message_history:
            merged_message_history = client_message_history
        else:
            only_system_messages = [msg for msg in message_history if msg.get("role", "system") == "system"]
            if len(only_system_messages) == len(message_history):
                merged_message_history = message_history + client_message_history
            else:
                merged_message_history = message_history

        # print("message_history:")
        # pprint(message_history)
        # print("-----------------------------------\n\n\n")
        # print("client_message_history:")
        # pprint(client_message_history)
        # print("-----------------------------------\n\n\n")
        # print(f"merged_message_history:")
        # pprint(merged_message_history)
        return merged_message_history


    async def generate_text(self, websocket: WebSocket, data: dict):
        """The actual text generation logic."""
        input_text = data.get("data", "")
        client_message_history = data.get("message_history", [])
        sid = str(websocket.client)
        token = self.sid_to_tokens.get(sid, None)
        if token is None:
            logger.error("Invalid token. Closing connection.")
            return
        
        user = self.credentials_manager.get_user_by_token(token)
        username = user.get("username", token)
        ai_instance = self.get_ai_instance(username, context=self.get_context(token))
        merged_message_history = self.merge_client_message_history(ai_instance.ai_connector.get_messages(), client_message_history)
        ai_instance.ai_connector.set_messages(merged_message_history)
        processed_prompt = self.preprocess_prompt(ai_instance, 
                                                  input_text, 
                                                  prompt_tools=self.get_prompt_tools_instance(username, context=self.get_context(token)))
        if processed_prompt.get("status", "noop") == "error":
            await websocket.send_text(json.dumps(processed_prompt))
            return
        prompt = processed_prompt.get("prompt", '')
        if prompt == '':
            return
        try:
            if prompt is not None:
                ai_instance.ai_connector.messages.append({"role": "user", "content": prompt})
            no_content = True
            while no_content:
                stream = ai_instance.ai_connector.get_stream()
                for content in ai_instance.ai_connector.process_stream(stream):
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
        token = self.sid_to_tokens.get(sid, None)
        user = self.credentials_manager.get_user_by_token(token)
        username = user.get("username", token)
        if token:
            self.clear_ai_instance(username)
            self.clear_prompt_tools_instance(username)
            self.sid_to_tokens.pop(sid, None)
            self.token_to_sids.pop(token, None)


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


    def get_ai_instance(self, username, context:dict={}) -> TAGAI:
        if username not in self.ai_instances:
            self.ai_instances[username] = self.ai_factory.create_ai_instance(context=context)
        return self.ai_instances[username]
    

    def clear_ai_instance(self, username):
        if username in self.ai_instances:
            del self.ai_instances[username]


    def get_prompt_tools_instance(self, username, context:dict={}) -> PromptTools:
        if username not in self.prompt_tools_instances:
            self.prompt_tools_instances[username] = self.create_prompt_tools_instance(context=context)
        return self.prompt_tools_instances[username]
    

    def clear_prompt_tools_instance(self, username):
        if username in self.prompt_tools_instances:
            del self.prompt_tools_instances[username]


    def create_prompt_tools_instance(self, context:dict={}) -> PromptTools:
        prompt_tools = None
        if self.prompt_tools_factory is not None:
            if isinstance(self.prompt_tools_factory, MechanicianToolsFactory):
                return self.prompt_tools_factory.create_tools(context=context)

            elif isinstance(self.prompt_tools_factory, MechanicianTools):
                return self.prompt_tools_factory
            
            elif isinstance(self.prompt_tools_factory, list):
                prompt_tools_instances = []
                for tool in self.prompt_tools_factory:
                    if isinstance(tool, MechanicianToolsFactory):
                        prompt_tools_instances.append(tool.create_tools(context=context))
                    elif isinstance(tool, PromptTools):
                        prompt_tools_instances.append(tool)
                    else:
                        raise ValueError(f"prompt_tools_factory must be an instance of or list of MechanicianToolsFactory. Received: {tool}")      
                return PromptToolKit(tools=prompt_tools_instances)
            else:
                raise ValueError(f"prompt_tools_factory must be an instance of or a list of MechanicianToolsFactory. Received: {self.prompt_tools_factory}")

            
    

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
        


    

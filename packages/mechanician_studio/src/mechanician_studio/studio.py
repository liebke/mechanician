from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect, status, Depends, HTTPException, File, Form, UploadFile, HTTPException
from datetime import datetime
from fastapi.templating import Jinja2Templates
from mechanician import AI, AIProvisioner
from typing import Dict
import json
import asyncio
import pkg_resources
from mechanician.tools import PromptTools, MechanicianTools, PromptToolKit, MechanicianToolsProvisioner, PromptPreprocessor, PromptPreprocessorProvisioner
import os
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import Response, RedirectResponse
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from mechanician_studio.auth import CredentialsManager, BasicCredentialsManager
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import logging
from pprint import pprint
from typing import List
import traceback
from mechanician_studio.datastores import UserDataStore, UserDataFileStore
from mechanician.events import EventProcessor, EventHandler
from mechanician_studio.resource_handlers import TextResourceUploadedEventHandler

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
    dev_ui_active: str

class UserUpdate(BaseModel):
    name: str
    username: str
    password: str
    new_password: str
    confirm_new_password: str
    user_role: str
    dev_ui_active: str

  
###############################################################################
## MechanicianWebApp class
###############################################################################
 
class AIStudio:
    stop_generation = False

    def __init__(self, 
                 ai_provisioners: List['AIProvisioner'],
                 event_handlers: Dict[str, List[EventHandler]]=None,
                 prompt_preprocessor_provisioners: Dict[str, PromptPreprocessorProvisioner]=None,
                 prompt_tools_provisioners=None,
                 credentials_manager: CredentialsManager=None,
                 credentials_file_path="./credentials.json",
                 dm_admin_username=None,
                 dm_admin_password=None,
                 user_data_store: UserDataStore=None,
                 user_data_file_path="./data"):
        
        if user_data_store is None:
            self.user_data_store = UserDataFileStore(user_data_file_path)
        else:
            self.user_data_store = user_data_store
        
        if ai_provisioners is None:
            raise ValueError("ai_provisioners must be provided")
        
        self.ai_provisioners = ai_provisioners
        self.prompt_tools_provisioners = prompt_tools_provisioners
        # create a list of AI names
        self.ai_names = []
        for aip in self.ai_provisioners:
            self.ai_names.append(aip.name)
        self.credentials_manager = credentials_manager or BasicCredentialsManager(credentials_filename=credentials_file_path)
        dm_admin_username = dm_admin_username or os.getenv("DM_ADMIN_USERNAME", "mechanician")
        if not self.credentials_manager.user_exists(dm_admin_username):
            dm_admin_password = dm_admin_password or os.getenv("DM_ADMIN_PASSWORD", None)
            if dm_admin_password is None:
                raise ValueError("dm_admin_password must be provided or DM_ADMIN_PASSWORD environment variable must be set.")
            else:
                admin_attrs = {"user_role": "Admin", "name": "Mechanician Admin"}
                self.credentials_manager.add_credentials(dm_admin_username, dm_admin_password, admin_attrs)

        self.app = FastAPI()
        template_directory = pkg_resources.resource_filename('mechanician_studio', 'templates')
        static_files_directory = pkg_resources.resource_filename('mechanician_studio', 'static')
        self.templates = Jinja2Templates(directory=template_directory)
        self.app.mount("/static", StaticFiles(directory=static_files_directory), name="static")
        self.ai_instances: Dict[str, AI] = {}
        self.prompt_tools_instances: Dict[str, PromptTools] = {}
        self.prompt_preprocessor_instances: Dict[str, PromptPreprocessor] = {}
        self.setup_routes()
        self.setup_websocket_events()

        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.sid_to_tokens: Dict[WebSocket, str] = {}
        self.token_to_sids: Dict[str, str] = {}

        if event_handlers is None:
            self.event_handlers = {"resource_uploaded": [TextResourceUploadedEventHandler()]}
        elif "resource_uploaded" not in event_handlers:
            self.event_handlers["resource_uploaded"] = [TextResourceUploadedEventHandler()]
        else:
            self.event_handlers = event_handlers

        self.event_processor = EventProcessor(self)

        self.prompt_preprocessor_provisioners = prompt_preprocessor_provisioners or {}



    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)
    

    def setup_routes(self):

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # EVENT PROCESSOR
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        @self.app.on_event("startup")
        async def startup_event():
            # Register handlers
            # Example: processor.register_handler('info', InfoEventHandler())
            # Example: processor.register_handler('error', ErrorEventHandler())
            # register event handlers using self.event_handlers
            for event_type, handlers in self.event_handlers.items():
                for handler in handlers:
                    self.event_processor.register_handler(event_type, handler)

            await self.event_processor.start()


        @self.app.on_event("shutdown")
        async def shutdown_event():
            await self.event_processor.stop()


        @self.app.post("/events/")
        async def create_event(event: dict):
            await self.event_processor.add_event(event)
            return {"message": "Event added successfully"}


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET / ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/", response_class=HTMLResponse)
        async def index_get(request: Request):
            user = self.credentials_manager.get_user_by_token(request.cookies.get("access_token"))
            if user is None:
                return self.templates.TemplateResponse("login.html", 
                                                       {"request": request})
            username = user.get("username", "")
            user_role = user.get("user_role", "User")
            dev_ui_active = user.get("dev_ui_active", False)

            # get ai_name from query parameter
            ai_name = request.query_params.get("ai_name")
            if ai_name is None:
                ai_name = self.ai_names[0]

            new_conversation = request.query_params.get("new_conversation")
            conversation_id = request.query_params.get("conversation_id")
            if conversation_id is None:
                if new_conversation != "true":
                    conversation_id = self.user_data_store.get_most_recent_conversation_id(username, ai_name)

            if conversation_id is None:
                conversation_id = self.user_data_store.new_conversation(username, ai_name)                    

            return self.templates.TemplateResponse("index.html", 
                                                   {"request": request,
                                                    "ai_names": self.ai_names,
                                                    "ai_name": ai_name,
                                                    "username": username,
                                                    "user_role": user_role,
                                                    "conversation_id": conversation_id,
                                                    "name": user.get("name", username),
                                                    "dev_ui_active": dev_ui_active})
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST / ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
            prompt = form_data_dict.get("_prompt", "")
            ai_name = form_data_dict.get("ai_name")
            dev_ui_active = user.get("dev_ui_active", False) #or form_data_dict.get("dev_ui_active", False)
            new_conversation = request.query_params.get("new_conversation")
            conversation_id = request.query_params.get("conversation_id")
            if conversation_id is None:
                if new_conversation != "true":
                    conversation_id = self.user_data_store.get_most_recent_conversation_id(username, ai_name)

            if conversation_id is None:
                conversation_id = self.user_data_store.new_conversation(username, ai_name)

            return self.templates.TemplateResponse("index.html", 
                                                   {"request": request,
                                                    "ai_names": self.ai_names,
                                                    "dev_ui_active": dev_ui_active,
                                                    "ai_name": ai_name,
                                                    "conversation_id": conversation_id,
                                                    "username": username,
                                                    "name": user.get("name", username),
                                                    "prompt": prompt,})
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST /upload_resource ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        @self.app.post("/upload_resource")
        async def upload_resource(request: Request, 
                                  file: UploadFile = File(...), 
                                  ai_name: str = Form(...),
                                  conversation_id: str = Form(...)):
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            username = user.get("username", access_token)  # Get username from user info or use access token

            resource_entry = await self.user_data_store.add_resource_file(username, ai_name, conversation_id, file, attributes = {})
            event = {"type": "resource_uploaded", "resource_entry": resource_entry}
            await self.event_processor.add_event(event)
            return JSONResponse(status_code=200, content={"message": "File uploaded successfully",
                                                          "resource_entry": resource_entry})


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST /call_prompt_tool ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.post("/call_prompt_tool", response_class=HTMLResponse)
        async def call_prompt_tool(request: Request):
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            form_data = await request.form()
            form_data_dict = dict(form_data)
            function_name = form_data_dict.get("function_name", "")
            prompt_template = form_data_dict.get("prompt_template", "")
            # remove function_name, prompt_template from form_data_dict
            form_data_dict.pop("function_name", None)
            form_data_dict.pop("prompt_template", None)
            username = user.get("username", access_token)
            ai_name = form_data_dict.get("ai_name")
            prompt_tools=self.get_prompt_tools_instance(username, ai_name, context=self.get_context(access_token, ai_name=ai_name))
            generated_prompt = prompt_tools.generate_prompt(function_name, prompt_template, params=form_data_dict)
            return JSONResponse(content=generated_prompt)
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST /call_ai_tool ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.post("/call_ai_tool", response_class=HTMLResponse)
        async def call_ai_tool(request: Request):
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            form_data = await request.form()
            form_data_dict = dict(form_data)
            function_name = form_data_dict.get("function_name", "")
            # remove function_name, prompt_template from form_data_dict
            form_data_dict.pop("function_name", None)
            username = user.get("username", access_token)
            ai_name = form_data_dict.get("ai_name")
            conversation_id = form_data_dict.get("conversation_id")
            ai_instance=self.get_ai_instance(username=username, 
                                             ai_name=ai_name,
                                             conversation_id=conversation_id,
                                             context=self.get_context(access_token, ai_name=ai_name))
            ai_tools = ai_instance.ai_tools
            response = ai_tools.call_function(function_name, params=form_data_dict)
            return JSONResponse(content=response)
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /list_resources ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/list_resources", response_class=HTMLResponse)
        async def list_resources(request: Request):
            
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            username = user.get("username", access_token)
            ai_name = request.query_params.get("ai_name")
            conversation_ids = self.user_data_store.list_resources(username)
            return JSONResponse(content=conversation_ids)
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /resources/<USERNAME> ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/resources/{username}", response_class=HTMLResponse)
        async def resources(request: Request, username: str):
            try:
                self.verify_access_token(request)
            except Exception as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            display_name = user.get("name", username)
            ai_name = request.query_params.get("ai_name")
            conversation_id = request.query_params.get("conversation_id")
            return self.templates.TemplateResponse("resources.html",
                                                   {"request": request,
                                                    "ai_names": self.ai_names,
                                                    "ai_name": ai_name,
                                                    # coversation_id for close button
                                                    "conversation_id": conversation_id,
                                                    "username": username,
                                                    "name": display_name})
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # DELETE /resources//<USERNAME>/<RESOURCE_ID> ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.delete("/resources/{username}/{resource_id}", response_class=HTMLResponse)
        async def delete_resource(request: Request, username: str, resource_id: str):
            try:
                self.verify_access_token(request)
            except Exception as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response

            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")
            
            result = self.user_data_store.delete_resource(username, resource_id)

            if not result:
                raise HTTPException(status_code=404, detail="Resource not found")

            # Redirect or respond after deletion. Adjust based on your application's flow.
            # For example, redirecting back to the conversations list:
            return RedirectResponse(url=f"/resources/{username}?ai_name={request.query_params.get('ai_name')}", status_code=status.HTTP_303_SEE_OTHER)


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /resources//<USERNAME>/<RESOURCE_ID> ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/resources/{username}/{resource_id}", response_class=HTMLResponse)
        async def get_resource(request: Request, username: str, resource_id: str):
            try:
                self.verify_access_token(request)
            except Exception as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response

            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")
            
            file = self.user_data_store.get_resource_data(username, resource_id)

            if not file:
                raise HTTPException(status_code=404, detail="Resource not found")

            resource_entry = self.user_data_store.get_resource_entry(username, resource_id)
            file_path = resource_entry.get("file_path")
            if not file_path:
                raise HTTPException(status_code=404, detail="Resource not found")

            # Return the file response
            return FileResponse(path=file_path, filename=f"{resource_id}")


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /conversation_history ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/conversation_history", response_class=HTMLResponse)
        async def conversation_history(request: Request):
            
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            username = user.get("username", access_token)
            ai_name = request.query_params.get("ai_name")
            conversation_id = request.query_params.get("conversation_id")
            history = self.user_data_store.get_conversation_history(username, ai_name, conversation_id)
            if not history:
                conversation_id = self.user_data_store.get_most_recent_conversation_id(username, ai_name)
                history = self.user_data_store.get_conversation_history(username, ai_name, conversation_id)
            response = {"conversation_id": conversation_id, "conversation_history": history}
            return JSONResponse(content=response)
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /list_conversations ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/list_conversations", response_class=HTMLResponse)
        async def list_conversations(request: Request):
            
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            username = user.get("username", access_token)
            ai_name = request.query_params.get("ai_name")
            conversation_ids = self.user_data_store.list_conversations(username, ai_name)
            return JSONResponse(content=conversation_ids)
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /conversations ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/conversations", response_class=HTMLResponse)
        async def conversations(request: Request):
            try:
                self.verify_access_token(request)
            except Exception as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            username = user.get("username", access_token)
            display_name = user.get("name", username)
            ai_name = request.query_params.get("ai_name")
            conversation_id = request.query_params.get("conversation_id")
            return self.templates.TemplateResponse("conversations.html",
                                                   {"request": request,
                                                    "ai_names": self.ai_names,
                                                    "ai_name": ai_name,
                                                    # coversation_id for close button
                                                    "conversation_id": conversation_id,
                                                    "username": username,
                                                    "name": display_name})
        


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # DELETE /conversations/<CONVERSATION_ID> ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.delete("/conversations/{ai_name}/{conversation_id}", response_class=HTMLResponse)
        async def delete_conversation(request: Request, ai_name: str, conversation_id: str):
            try:
                self.verify_access_token(request)
            except Exception as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response

            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")
            
            username = user.get("username", access_token)
            result = self.user_data_store.delete_conversation(username, ai_name, conversation_id)

            if not result:
                raise HTTPException(status_code=404, detail="Conversation not found")

            # Redirect or respond after deletion. Adjust based on your application's flow.
            # For example, redirecting back to the conversations list:
            return RedirectResponse(url=f"/conversations?ai_name={request.query_params.get('ai_name')}", status_code=status.HTTP_303_SEE_OTHER)

        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /get_ai_settings ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/get_ai_settings", response_class=HTMLResponse)
        async def get_ai_settings(request: Request):
            
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            username = user.get("username", access_token)
            ai_name = request.query_params.get("ai_name")
            conversation_id = request.query_params.get("conversation_id")
            ai_instance = self.get_ai_instance(username=username, 
                                               ai_name=ai_name,
                                               conversation_id=conversation_id,
                                               context=self.get_context(access_token, ai_name=ai_name))
            ai_instructions=ai_instance.ai_instructions
            ai_tool_instructions=ai_instance.ai_tool_instructions
            response = {"ai_instructions": ai_instructions, "ai_tool_instructions": ai_tool_instructions}
            return JSONResponse(content=response)
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /ai_settings ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/ai_settings", response_class=HTMLResponse)
        async def ai_settings(request: Request):
            try:
                self.verify_access_token(request)
            except Exception as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            access_token = request.cookies.get("access_token")
            user = self.credentials_manager.get_user_by_token(access_token)
            if user is None:
                raise HTTPException(status_code=401, detail="Unauthorized: Invalid credentials")

            username = user.get("username", access_token)
            display_name = user.get("name", username)
            ai_name = request.query_params.get("ai_name")
            conversation_id = request.query_params.get("conversation_id")
            return self.templates.TemplateResponse("ai_settings.html",
                                                   {"request": request,
                                                    "ai_names": self.ai_names,
                                                    "ai_name": ai_name,
                                                    # coversation_id for close button
                                                    "conversation_id": conversation_id,
                                                    "username": username,
                                                    "name": display_name})
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST /token ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /login ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/login")
        async def login(request: Request):
            return self.templates.TemplateResponse("login.html", 
                                                   {"request": request})
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /create_user ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
           
            username = user.get("username", "anonymous")
            display_name = user.get("name", username)
            dev_ui_active = user.get("dev_ui_active", "False")
            
            if user.get("user_role", "User") != "Admin":
                response = RedirectResponse(url='/', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            ai_name = request.query_params.get("ai_name")
            conversation_id = request.query_params.get("conversation_id")
            
            return self.templates.TemplateResponse("create_user.html",
                                                   {"request": request,
                                                    "ai_names": self.ai_names,
                                                    "ai_name": ai_name,
                                                    "conversation_id": conversation_id,
                                                    "username": username,
                                                    "name": display_name,
                                                    "dev_ui_active": dev_ui_active})
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST /create_user ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
            attrs = {"user_role": user.user_role, 
                     "name": user.name,
                     "dev_ui_active": user.dev_ui_active}
            create_status = self.credentials_manager.add_credentials(user.username, user.password, attrs)
            if not create_status:
                raise HTTPException(status_code=400, detail="User already exists")

            return {"message": "User created successfully"}
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /user ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
                dev_ui_active = user_data.get("dev_ui_active", False)

            except HTTPException as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response
            
            ai_name = request.query_params.get("ai_name")
            conversation_id = request.query_params.get("conversation_id")
            
            return self.templates.TemplateResponse("user.html", 
                                                   {"request": request,
                                                    "username": username,
                                                    "ai_names": self.ai_names,
                                                    "ai_name": ai_name,
                                                    "conversation_id": conversation_id,
                                                    "name": display_name,
                                                    "user_role": user_role,
                                                    "dev_ui_active": dev_ui_active})
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST /user ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
                                                                            attributes={"name": user.name,
                                                                                        "user_role": user.user_role,
                                                                                        "dev_ui_active": user.dev_ui_active})
            if not update_status:
                logger.error("User attribute update error")
                raise HTTPException(status_code=400, detail="User attribute update error")

            return {"message": "User update successfully"}
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST /logout ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.post("/logout")
        def logout():
            logger.debug("Logging out...")
            response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
            response.delete_cookie(key="access_token")
            return response
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST /new ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.post("/new")
        def new_session(request: Request):
            logger.debug("Starting new session...")
            # get token from cookie
            token = request.cookies.get("access_token")
            # get sid from token
            sid = self.token_to_sids.get(token, None)
            user = self.credentials_manager.get_user_by_token(token)
            username = user.get("username", token)
            ai_name = request.query_params.get("ai_name")
            # clear ai instance
            if sid:
                self.clear_ai_instance(username)

            response = RedirectResponse(url='/?new_conversation=true', status_code=status.HTTP_303_SEE_OTHER)
            return response
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /ai_tools ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/ai_tools")
        async def ai_tools(request: Request):
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

            ai_name = request.query_params.get("ai_name")
            conversation_id = request.query_params.get("conversation_id")
            return self.templates.TemplateResponse("ai_tools.html", 
                                                   {"request": request,
                                                    "username": username,
                                                    "ai_names": self.ai_names,
                                                    "ai_name": ai_name,
                                                    "conversation_id": conversation_id, 
                                                    "name": display_name,
                                                    "user_role": user_role})


        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /list_ai_tools ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.get("/list_ai_tools")
        async def list_ai_tools(request: Request):
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
            
            ai_name = request.query_params.get("ai_name") or self.ai_names[0]
            conversation_id = request.query_params.get("conversation_id")
            token = request.cookies.get("access_token")
            ai_instance = self.get_ai_instance(username, 
                                               ai_name, 
                                               conversation_id=conversation_id, 
                                               context=self.get_context(token, ai_name=ai_name))
            if ai_instance is None:
                return JSONResponse(content={"error": "No AI instance found."})
            
            ai_tool_instructions = ai_instance.ai_tool_instructions
            if ai_tool_instructions is None:
                return JSONResponse(content={"error": "No function name provided."})
            else:
                return JSONResponse(content=ai_tool_instructions)
            

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /prompt_tools ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
                dev_ui_active = user_data.get("dev_ui_active", False)
                if dev_ui_active == "True":
                    prompt_template = "dev_prompt_tools.html"
                else:
                    prompt_template = "user_prompt_tools.html"

            except HTTPException as e:
                logger.error(f"Error validating token: {e}")
                response = RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)
                return response

            token = request.cookies.get("access_token")
            ai_name = request.query_params.get("ai_name") or self.ai_names[0]
            prompt_tools=self.get_prompt_tools_instance(username, ai_name, context=self.get_context(token, ai_name=ai_name))
            conversation_id = request.query_params.get("conversation_id")
            return self.templates.TemplateResponse(prompt_template, 
                                                   {"request": request,
                                                    "prompt_tool_instructions": prompt_tools.get_tool_instructions(),
                                                    "username": username,
                                                    "ai_names": self.ai_names,
                                                    "ai_name": ai_name,
                                                    "conversation_id": conversation_id,
                                                    "name": display_name,
                                                    "user_role": user_role})
        

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # GET /prompt_tools/templates/{template_name} ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
            ai_name = request.query_params.get("ai_name") or self.ai_names[0]
            username = user_data.get("username", None)
            if username is None:
                return JSONResponse(content={"error": "No username provided."})
            
            # get prompt template name from url path
            template_name = request.path_params.get("template_name", None)
            token = request.cookies.get("access_token")
            prompt_tools=self.get_prompt_tools_instance(username, ai_name, context=self.get_context(token, ai_name=ai_name))
            if template_name is None:
                return JSONResponse(content={"error": "No prompt template name provided."})
            else:
                prompt_template = prompt_tools.get_prompt_template(prompt_template_name=template_name).template_str
                return JSONResponse(content=prompt_template)
            

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # POST /prompt_tools/resources ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.post("/prompt_tools/resources")
        async def prompt_tools_resources(request: Request):
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
            
            form_data = await request.form()
            form_data_dict = dict(form_data)
            function_name = form_data_dict.get("function_name", "")
            ai_name = form_data_dict.get("ai_name")
            token = request.cookies.get("access_token")
            prompt_tools=self.get_prompt_tools_instance(username, ai_name, context=self.get_context(token, ai_name=ai_name))
            if function_name is None:
                return JSONResponse(content={"error": "No function name provided."})
            else:
                resources = prompt_tools.get_resources(function_name=function_name, params=form_data_dict)
                return JSONResponse(content=resources)

        

    def setup_websocket_events(self):

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # WEBSOCKET /ws ROUTE
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            logger.debug("WebSocket connection accepted")
            sid = str(websocket.client)
            try:
                # Authentication (Assuming this is a separate method for clarity)
                auth = await self.authenticate_websocket(websocket)
                if not auth.get("authorized", False):
                    logger.info("Authentication failed")
                    return
                
                # Main WebSocket communication loop
                while True:
                    await self.handle_incoming_messages(websocket, 
                                                        ai_name=auth.get("ai_name", None),
                                                        conversation_id=auth.get("conversation_id", None))
            except WebSocketDisconnect:
                logger.info("Client disconnected")
                self.cleanup(sid)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                self.cleanup(sid)



    async def authenticate_websocket(self, websocket: WebSocket) -> bool:
        """Handle authentication for the WebSocket connection."""
        try:
            auth_data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
            auth_data = json.loads(auth_data)
            token = auth_data.get("token", "")
            ai_name = auth_data.get("ai_name", None)
            if ai_name is None or ai_name == "":
                ai_name = self.ai_names[0]
            conversation_id = auth_data.get("conversation_id", "")
            new_conversation = auth_data.get("new_conversation", False)
            if new_conversation:
                conversation_id = self.user_data_store.new_conversation(token, ai_name)

            sid = str(websocket.client)
            self.token_to_sids[token] = sid
            self.sid_to_tokens[sid] = token
            if self.credentials_manager.verify_access_token(token):
                logger.debug("Token verified")
                resp = {"role": "system",
                        "ai_name": ai_name,
                        "conversation_id": conversation_id,
                        "authorized": True,
                        "content": f"Authentication successful. You are now connected to \"{ai_name}\".\n\n"}
                await websocket.send_text(json.dumps(resp))
                await asyncio.sleep(0)
                return resp
            else:
                logger.info("Invalid token. Closing connection.")
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return {"authorized": False}
        except asyncio.TimeoutError:
            logger.info("Authentication timeout. Closing connection.")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return {"authorized": False}
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            self.cleanup(sid)
            return {"authorized": False}


    async def handle_incoming_messages(self, 
                                       websocket: WebSocket,
                                       ai_name: str=None,
                                       conversation_id: str=None):
        """Process incoming WebSocket messages."""
        async for message in websocket.iter_text():
            data = json.loads(message)
            input_type = data.get("type", "")
            if input_type == "stop":
                await self.stop_text_generation(websocket)
            else:
                await self.start_text_generation(websocket, 
                                                 data,
                                                 ai_name=ai_name,
                                                 conversation_id=conversation_id)


    async def start_text_generation(self, websocket: WebSocket, 
                                    data: dict,
                                    ai_name: str=None,
                                    conversation_id: str=None):
        """Starts the text generation process in a separate task."""
        sid = str(websocket.client)
        if sid in self.active_tasks:
            self.active_tasks[sid].cancel()
        self.active_tasks[sid] = asyncio.create_task(self.generate_text(websocket, 
                                                                        data,
                                                                        ai_name=ai_name,
                                                                        conversation_id=conversation_id))


    def get_context(self, token:str, ai_name:str=None):
        user = self.credentials_manager.get_user_by_token(token)
        access_token_data = self.credentials_manager.decode_access_token(token)
        return {"username": user.get("username", ""), 
                "user_role": user.get("user_role", "User"), 
                "access_token_data": access_token_data,
                "ai_name": ai_name}
    

    # def merge_client_message_history(self, message_history, client_message_history):
    #     merged_message_history = []
    #     if not message_history:
    #         merged_message_history = client_message_history
    #     else:
    #         only_system_messages = [msg for msg in message_history if msg.get("role", "system") == "system"]
    #         if len(only_system_messages) == len(message_history):
    #             merged_message_history = message_history + client_message_history
    #         else:
    #             merged_message_history = message_history

    #     return merged_message_history


    async def generate_text(self, websocket: WebSocket, 
                            data: dict,
                            ai_name: str=None,
                            conversation_id: str=None):
        """The actual text generation logic."""
        input_text = data.get("data", "")
        # ai_name = data.get("ai_name", "")
        # conversation_id = data.get("conversation_id", None)
        sid = str(websocket.client)
        token = self.sid_to_tokens.get(sid, None)
        if token is None:
            logger.error("Invalid token. Closing connection.")
            return
        
        if conversation_id is None or conversation_id == "":
            conversation_id = self.user_data_store.get_most_recent_conversation_id(token, ai_name)
            if conversation_id is None or conversation_id == "":
                conversation_id = self.user_data_store.new_conversation(token, ai_name)

        user = self.credentials_manager.get_user_by_token(token)
        username = user.get("username", token)
        ai_instance = self.get_ai_instance(username=username, 
                                           ai_name=ai_name,
                                           conversation_id=conversation_id,
                                           context=self.get_context(token, ai_name=ai_name))
        prompt_preprocessor = self.get_prompt_preprocessor_instance(username, 
                                                                    ai_name, 
                                                                    context=self.get_context(token, ai_name=ai_name))
        if prompt_preprocessor is not None:
            processed_prompt = prompt_preprocessor.preprocess_prompt(input_text)
            if processed_prompt.get("status", None) == "error":
                resp = {"role": "assistant", "content": json.dumps(processed_prompt)}
                await websocket.send_text(json.dumps(resp))
                await asyncio.sleep(0)
                return
            
            prompt = processed_prompt.get("prompt", '')
        else:
            prompt = input_text

        if prompt == '':
            return
        try:
            if prompt is not None:
                msg = {"role": "user", "content": prompt}
                self.user_data_store.append_message_to_conversation(username, ai_name, conversation_id, msg)
                ai_instance.ai_connector.messages.append(msg)
            no_content = True
            while no_content:
                stream = ai_instance.ai_connector.get_stream()
                ai_response = ""
                msg = None
                for content in ai_instance.ai_connector.process_stream(stream):
                    if self.stop_generation:
                        self.stop_generation = False
                        break

                    if content is None:
                        no_content = True
                        break
                    else:
                        no_content = False
                        # If content is a dictionary, it is a tool call or end of stream response
                        if isinstance(content, dict):
                            if "finish_reason" in content:
                                print(f"Finish Reason: {content.get('finish_reason')}")
                                if content.get("finish_reason") == "stop":
                                    await websocket.send_text(json.dumps({"role": "assistant", 
                                                                          "content": None, 
                                                                          "finish_reason": "stop",
                                                                          "ai_name": ai_name,
                                                                          "conversation_id": conversation_id}))
                                    await asyncio.sleep(0)
                            elif ("tool_call_id" in content) or ("tool_calls" in content): # tool call response or tool call
                                tool_msg = self.format_tool_call_messages(content)
                                content = tool_msg.get("content", "")
                                self.user_data_store.append_message_to_conversation(username, ai_name, conversation_id, tool_msg)
                                if user.get("dev_ui_active", "False") == "True":
                                    tool_msg["ai_name"] = ai_name
                                    tool_msg["conversation_id"] = conversation_id
                                    await websocket.send_text(json.dumps(tool_msg))
                                    await asyncio.sleep(0)
                            else:
                                # await websocket.send_text(json.dumps({"role": "assistant", "content": content}))
                                await websocket.send_text(json.dumps(content))
                                await asyncio.sleep(0)
                                ai_response += content.get("content", "")
                                msg = {"role": "assistant", 
                                       "content": ai_response,
                                       "ai_name": ai_name,
                                       "conversation_id": conversation_id}

                if msg is not None:
                    self.user_data_store.append_message_to_conversation(username, ai_name, conversation_id, msg)

        except asyncio.CancelledError:
            logger.info("Text generation cancelled.")
        except Exception as e:
            logger.error(f"Error processing AI response: {e}")
            await websocket.send_text(json.dumps({"error": str(e)}))
            traceback.print_exc()


    def format_tool_call_messages(self, content):
        output_str = ""
        msg = None
        if isinstance(content, dict):
            role = content.get("role", None)
            if role == "assistant" and "tool_calls" in content:
                tool_calls = content.get("tool_calls")
                for tool_call in tool_calls:
                    func = tool_call.get("function")
                    args = "<pre><code>"
                    args += json.dumps(json.loads(func.get("arguments")), indent=4)
                    args += "</code></pre>"
                    output_str += f"""<b>Function Called</b>: {func.get("name")}\n<b>ID</b>: {tool_call.get("id")}\n<b>Arguments</b>:\n{args}\n"""
                    msg = {"role": role, 
                           "tool_calls": tool_calls,
                           "tool_call_id": tool_call.get("id"),
                           "content": output_str}
            elif role == "tool":
                output_str += f"""<b>Function Response</b>: {content.get("name")}\n"""
                output_str += f"""<b>ID</b>: {content.get("tool_call_id")}\n"""
                resp = content.get("content")
                
                output_str += "<b>Response</b>: \n"
                if isinstance(resp, dict):
                    output_str += json.dumps(resp, indent=4)
                else:
                    json_resp = json.loads(resp)
                    output_str += f"<pre><code>{json.dumps(json_resp, indent=4)}</code></pre>"
                output_str += "\n"
                msg = {"role": role, 
                       "tool_call_id": content.get("tool_call_id"),
                       "content": output_str}
            else:
                output_str += f"<b>Unknown Role</b>: {role}\n"
                output_str += f"<b>Content</b>: {content}\n"
                msg = {"role": role, "content": output_str}
                
            return msg


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
            self.clear_prompt_preprocessor_instance(username)
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

    def get_ai_instance(self, username:str, ai_name:str, conversation_id:str, context:dict={}) -> AI:
        if username not in self.ai_instances:
            # get ai provisioner by name
            ai_provisioner = None
            for aip in self.ai_provisioners:
                if aip.name == ai_name:
                    ai_provisioner = aip
                    break

            # If conversation_id is not None, get message history from UserDataStore
            if conversation_id is not None:
                conversation_history = self.user_data_store.get_conversation_history(username, ai_name, conversation_id)
                if conversation_history:
                    context["conversation_history"] = conversation_history
                ai_instance = ai_provisioner.create_ai_instance(context=context)
            else:
                # Create new conversation in UserDataStore
                conversation_id = self.user_data_store.new_conversation(username, ai_name)
                # IF NEW CONVERSATION, LOOK FOR CUSTOM INSTRUCTIONS
                ai_instructions = self.user_data_store.get_ai_instructions(username, ai_name) # DEFAULT IS NONE
                ai_tool_instructions = self.user_data_store.get_ai_tool_instructions(username, ai_name) # DEFAULT IS NONE
                context["ai_instructions"] = ai_instructions
                context["ai_tool_instructions"] = ai_tool_instructions
                ai_instance = ai_provisioner.create_ai_instance(context=context)
                # Get initial system message from AI
                conversation_history = ai_instance.ai_connector.get_messages()
                self.user_data_store.set_conversation_history(username, ai_name, conversation_id, conversation_history)
                        
        self.ai_instances[(username, ai_name)] = ai_instance
        return ai_instance
    

    def clear_ai_instance(self, username):
        keys = [key for key in self.ai_instances.keys() if key[0] == username]
        for key in keys:
            del self.ai_instances[key]


    def get_prompt_tools_instance(self, username:str, ai_name:str, context:dict={}) -> PromptTools:
        if (username, ai_name) not in self.prompt_tools_instances:
            self.prompt_tools_instances[(username, ai_name)] = self.create_prompt_tools_instance(context=context)
        return self.prompt_tools_instances[(username, ai_name)]
    

    def clear_prompt_tools_instance(self, username):
        keys = [key for key in self.prompt_tools_instances.keys() if key[0] == username]
        for key in keys:
            del self.prompt_tools_instances[key]


    def create_prompt_tools_instance(self, context:dict={}) -> PromptTools:
        prompt_tools = None
        if self.prompt_tools_provisioners is not None:
            if isinstance(self.prompt_tools_provisioners, MechanicianToolsProvisioner):
                return self.prompt_tools_provisioners.create_tools(context=context)

            elif isinstance(self.prompt_tools_provisioners, MechanicianTools):
                return self.prompt_tools_provisioners
            
            elif isinstance(self.prompt_tools_provisioners, list):
                prompt_tools_instances = []
                for tool in self.prompt_tools_provisioners:
                    if isinstance(tool, MechanicianToolsProvisioner):
                        prompt_tools_instances.append(tool.create_tools(context=context))
                    elif isinstance(tool, PromptTools):
                        prompt_tools_instances.append(tool)
                    else:
                        raise ValueError(f"prompt_tools_provisioner must be an instance of or list of MechanicianToolsProvisioner. Received: {tool}")      
                return PromptToolKit(tools=prompt_tools_instances)
            else:
                raise ValueError(f"prompt_tools_provisioner must be an instance of or a list of MechanicianToolsProvisioner. Received: {self.prompt_tools_provisioners}")

            
    def get_prompt_preprocessor_instance(self, username:str, ai_name:str, context:dict={}) -> PromptPreprocessor:
        provisioner = self.prompt_preprocessor_provisioners.get(ai_name, None)
        if provisioner is None:
            return None
        
        if (username, ai_name) not in self.prompt_preprocessor_instances:
            self.prompt_preprocessor_instances[(username, ai_name)] = self.create_prompt_preprocessor_instance(username, ai_name, context=context)
        return self.prompt_preprocessor_instances[(username, ai_name)]
    
    
    def clear_prompt_preprocessor_instance(self, username):
        keys = [key for key in self.prompt_preprocessor_instances.keys() if key[0] == username]
        for key in keys:
            del self.prompt_preprocessor_instances[key]


    def create_prompt_preprocessor_instance(self, username, ai_name, context:dict={}) -> PromptPreprocessor:
        if self.prompt_preprocessor_provisioners is not None:
            provisioner = self.prompt_preprocessor_provisioners.get(ai_name, None)
            if isinstance(provisioner, MechanicianToolsProvisioner):
                prompt_preprocessor = provisioner.create_tools(context=context)
                return prompt_preprocessor
            
            else:
                raise ValueError(f"prompt_preprocessor_provisioner must be an instance of or a list of MechanicianToolsProvisioner. Received: {provisioner}")


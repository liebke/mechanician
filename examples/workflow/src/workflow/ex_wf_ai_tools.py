from mechanician.ai_tools import AITools
from mechanician import TAGAI
from arango import ArangoClient
import json
from mechanician_arangodb.document_manager import DocumentManager
from mechanician_arangodb.document_ai_tools import DocumentManagerAITools
import logging
import pprint
from datetime import datetime
import os
import uuid
import random

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

###############################################################################
## RUN_WORKFLOW
###############################################################################

# def run_workflow(ai: 'TAGAI', workflow_name: str):
#     messages = []
#     workflow_tools = ai.tools
#     wf, task = workflow_tools.start_workflow({"workflow_name": workflow_name})
#     try:
#         # while not (workflow_tools.running_workflow is None):
#         while not (wf.get("COMPLETE", False) is True):
#             tasks = list(workflow_tools.running_tasks.values())
#             for task in tasks:
#                 print(f"\n\nSTARTING TASK {task['task_id']}:")
#                 task_id = task.get("task_id", None)
#                 print("\n\n")
#                 print("\nWORKFLOW:")
#                 pprint.pprint(task)
#                 print("\nASSISTANT:")
#                 assist_resp = ai.submit_prompt(json.dumps(task))
#                 messages.append(f"\nASSISTANT: {assist_resp}")
#                 if (not ai.streaming_connector()) and (assist_resp is not None):
#                     print(f"**ASSISTANT** {assist_resp}")
#                 print("\n\n")
#                 while not (workflow_tools.running_tasks.get(task_id, None) is None):
#                     wf_prompt = f"Complete task {task_id} by calling `get_next_task` with the `current_task_id` and a list of the `next` tasks to retrieve."
#                     print(f"\nWORKFLOW: {wf_prompt}")
#                     print("\nASSISTANT:")
#                     assist_resp = ai.submit_prompt(wf_prompt)
#                     messages.append(f"\nASSISTANT: {assist_resp}")
#                     if (not ai.streaming_connector()) and (assist_resp is not None):
#                         print(f"**ASSISTANT** {assist_resp}")

#     except KeyboardInterrupt:
#         print("Ctrl+C was pressed, exiting...")
#     except EOFError:
#         print("Ctrl+D was pressed, exiting...")
#     finally:
#         ai.clean_up()
#         print("goodbye")


class LTMAITools(AITools):

    def __init__(self,
                 userid: str,
                 arango_client: ArangoClient, 
                 database_name: str,
                 db_username: str = 'root' , 
                 db_password: str = None,
                 workflows = {}):
        #### Workflows ######
        self.WORKFLOW_RUNNING = False
        self.workflows = workflows
        self.workflow_executions = {}
        self.running_tasks = {}
        #### Memory #########
        self.userid = userid
        logger.info(f"Initializing LTMAITools with database_name: {database_name}")
        if not arango_client:
            raise ValueError("Arango client is required.")
        if not database_name:
            raise ValueError("Database name is required.")
        db_username = db_username or os.getenv("ARANGO_USERNAME", None)
        db_password = db_password or os.getenv("ARANGO_PASSWORD", None)
        if (not db_username) or (not db_password):
            raise ValueError("ARANGO_USERNAME and ARANGO_PASSWORD are required.")
        self.doc_mgr = DocumentManager(arango_client, db_username, db_password)
        self.database_name = database_name
        self.database = self.doc_mgr.create_database(database_name)
        # Create a collection for memories
        self.collection_name = f"memories"
        collection = self.doc_mgr.create_document_collection(self.database, self.collection_name)
        resp = f"Collection '{self.collection_name}' created."
        logger.info(pprint.pformat(resp))
        # Get the current user's memories
        self.memories = self.doc_mgr.get_document(self.database, self.collection_name, self.userid)
        logger.info(f"User '{self.userid}' memories")
        logger.info(pprint.pformat(self.memories))
        # Create a document for the current user's memories if it doesn't exist
        if not self.memories:
            self.doc_mgr.create_document(self.database, collection_name=self.collection_name, document_id=self.userid, document={})


###############################################################################
## WAG
###############################################################################

    def start_workflow(self, input: dict):
        self.WORKFLOW_RUNNING = True
        print("START_WORKFLOW INPUT:")
        pprint.pprint(input)
        wf_name = input.get("workflow_name", None)
        if wf_name is None:
            resp = "workflow_name is required."
            logger.info(resp)
            return resp
        workflow_ref = self.workflows.get(wf_name, None)
        if workflow_ref is None:
            resp = f"Workflow '{wf_name}' does not exist."
            logger.info(resp)
            return resp
        # create an instance of the workflow
        workflow = workflow_ref.copy()
        workflow_id = str(uuid.uuid4())
        workflow["workflow_id"] = workflow_id
        workflow["workflow_name"] = wf_name
        workflow["COMPLETE"] = False
        self.workflow_executions[workflow_id] = workflow
        start = workflow.get("start", None)
        if start is None:
            resp = f"Workflow '{wf_name}' has no start task."
            logger.info(resp)
            return resp
        instructions = start.get("instructions", None)
        decisions = start.get("decisions", None)
        if instructions is None and decisions is None:
            next = start.get("next", None)
            if next is None:
                resp = f"Workflow '{wf_name}' has no next task."
                logger.info(resp)
                return resp
            for task_name in next:
                resp = self.start_task({"workflow_id": workflow_id, "task_name": task_name, "input": input})
        else:
            resp = self.start_task({"workflow_id": workflow["workflow_id"],
                                    "task_name": "start", 
                                    "input": input})
        
        print("START WORKFLOW OUTPUT:")
        pprint.pprint(resp)
        return workflow, resp


    def start_task(self, input: dict):
        print("START_TASK INPUT:")
        pprint.pprint(input)
        task_name = input.get("task_name", None)
        if task_name is None:
            resp = "task_name is required."
            logger.info(resp)
            return resp
        
        workflow_id = input.get("workflow_id", None)
        wf_execution = self.workflow_executions.get(workflow_id, None)

        if wf_execution is None:
            resp = f"Workflow Execution {workflow_id} not found."
            logger.info(resp)
            return resp
        
        task = wf_execution.get(task_name, None)
        # print("START_TASK: TASK STARTING")
        # pprint.pprint(task)
        if task is None:
            resp = f"Task '{task_name}' does not exist."
            logger.info(resp)
            return resp
    
        # set task_id
        task_id = str(uuid.uuid4())
        task["COMPLETE"] = False
        task["task_id"] = task_id
        task["workflow_id"] = workflow_id
        self.running_tasks[task_id] = task

        print("START_TASK: TASK STARTED")
        pprint.pprint(task)
        return task

    # COMPLETES THE CURRENT TASK AND RETURNS THE NEXT TASK

    def get_next_task(self, input: dict):
        print("get_next_task INPUT:")
        pprint.pprint(input)
       
        current_task_id = input.get("current_task_id", None)
        if current_task_id is None:
            resp = "The current_task_id is a required parameter of `get_next_task`."
            logger.info(resp)
            return resp
        
        result = input.get("result", None)

        task = self.running_tasks.get(current_task_id, None)
        if task is None:
            resp = f"Task '{current_task_id}' is not running."
            logger.info(resp)
            return resp
        
        next = input.get("next", None)
        if (not task.get("next", None) is None) and (next is None):
            resp = "You must provide `next` tasks when the `current_task` has a `next` field."
            logger.info(resp)
            return resp

        # Complete the current task
        task["COMPLETE"] = True
        if result is not None:
            task["result"] = result
        # REMOVE FROM RUNNING TASKS
        self.running_tasks.pop(current_task_id)

        # Get next tasks
        workflow_id = task.get("workflow_id", None)
        wf_execution = self.workflow_executions.get(workflow_id, None)
        if wf_execution is None:
            resp = f"Workflow Execution {workflow_id} not found."
            logger.info(resp)
            return resp
        
        if (not next) or (next is None):
            if not self.running_tasks:
                resp = f"WORKFLOW COMPLETE."
                wf_execution["COMPLETE"] = True
                logger.info(resp)
                print(resp)
                return resp
            else:
                resp = f"Complete your remaining current Tasks, Workflow '{workflow_id}' is not complete yet."
                logger.info(resp)
                return resp
        else:
            next_tasks = []
            for next_task_name in next:
                next_task = self.start_task({"workflow_id": task["workflow_id"], 
                                            "task_name": next_task_name})
                # print("NEXT TASK:")
                # pprint.pprint(next_task)
                next_tasks.append(next_task)

            return next_tasks
        
        

###############################################################################
## END WAG
###############################################################################
             

    def get_weather(self, input: dict):
        location = input.get("location", "unknown")
        date = input.get("date", "unknown")
        if location == "unknown":
            resp = f"Sorry, I don't know where you are. Please provide a location."
            logger.info(resp)
            return resp
        
        if date == "unknown":
            resp = f"Sorry, I don't know when you want the weather for. Please provide a date."
            logger.info(resp)
            return resp
        weather_conditions = [{"weather": "sunny"}]
        weather_conditions = ['Sunny, 75F', 'Cloudy, 60F', 'Rainy, 50F', 'Snowy, 20F', 'Windy, 70F', 'Foggy, 55F', 'Hazy, 65F', 'Thunderstorms, 70F', 'Tornado, 80F', 'Hurricane, 85F', 'Tropical Storm, 75F', 'Blizzard, 30F', 'Ice Storm, 40F', 'Hail, 45F', 'Sleet, 35F', 'Freezing Rain, 40F', 'Dust Storm, 70F', 'Sand Storm, 75F', 'Mist, 55F', 'Drizzle, 50F', 'Showers, 55F', 'Flurries, 40F', 'Snow Showers, 35F', 'Snow, 30F', 'Sleet, 35F', 'Freezing Rain, 40F', 'Hail, 45F', 'Tornado, 80F', 'Hurricane, 85F', 'Tropical Storm, 75F', 'Blizzard, 30F', 'Ice Storm, 40F', 'Hail, 45F', 'Sleet, 35F', 'Freezing Rain, 40F', 'Dust Storm, 70F', 'Sand Storm, 75F', 'Mist, 55F', 'Drizzle, 50F', 'Showers, 55F', 'Flurries, 40F', 'Snow Showers, 35F', 'Snow, 30F', 'Sleet, 35F', 'Freezing Rain, 40F', 'Hail, 45F', 'Tornado, 80F', 'Hurricane, 85F', 'Tropical Storm, 75F', 'Blizzard, 30F', 'Ice Storm, 40F', 'Hail, 45F', 'Sleet, 35F', 'Freezing Rain, 40F', 'Dust Storm, 70F', 'Sand Storm, 75F', 'Mist, 55F', 'Drizzle, 50F', 'Showers, 55F', 'Flurries, 40F', 'Snow Showers, 35F', 'Snow, 30F', 'Sleet, 35F', 'Freezing Rain, 40F', 'Hail, 45F',]
        resp = random.choice(weather_conditions)
        logger.info(f"Getting weather for {input}")
        logger.info(pprint.pformat(resp))
        return resp


    def get_current_datetime(self, input: dict):
        current_datetime = datetime.now().isoformat()
        resp = {"current_datetime": current_datetime}
        return resp
    
    ###############################################################################
    ## LTM
    ###############################################################################
   

    def remember(self, input: dict):
        try:
            print("REMEMBER INPUT:")
            pprint.pprint(input)
            name = input.get('name', None)
            value = input.get('value', None)

            if (name is None):
                resp = "name is required."
                logger.info(resp)
                return resp
            
            if (value is None):
                resp = "value is required."
                logger.info(resp)
                return resp
            
            self.memories[name] = value
            doc = self.doc_mgr.add_field_to_document(self.database, self.collection_name, self.userid, name, value)
            resp = f"Memory '{name}' created for user '{self.userid}':"
            # DEBUG
            logger.debug(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def forget_memory(self, input: dict):
        try:
            print("DELETE_MEMORY INPUT:")
            pprint.pprint(input)
            memory_name = input.get('memory_name', None)

            if memory_name is None:
                resp = "memory_name is required."
                logger.info(resp)
                return resp

            removed_memory = self.memories.pop(memory_name, None)
            if removed_memory is not None:
                resp = f"Memory '{memory_name}' deleted."
            else:
                resp = f"Memory '{memory_name}' does not exist."

            # DEBUG
            logger.debug(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def recall_memories(self, input: dict):
        try:
            doc = self.doc_mgr.get_document(self.database, self.collection_name, self.userid)
            resp =  json.dumps(doc, indent=2)
            logger.debug(f"Memories for user '{self.userid}' in memory_collection '{self.collection_name}':")
            logger.debug(pprint.pformat(resp))
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def recall_memory(self, input: dict):
        try:
            memory = input.get('name', None)
            if (memory is None):
                resp = "name is required."
                logger.info(resp)
                return resp
                        
            memory = self.memories.get(memory, None)
            resp = f"Memory '{memory}' for user '{self.userid}' in memory_collection '{self.collection_name}': {memory}."
            # DEBUG
            logger.debug(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    ###############################################################################
    ## END LTM
    ###############################################################################
   
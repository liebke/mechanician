from mechanician.ai_tools import AITools
import logging
import pprint
import uuid

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


class WorkflowAITools(AITools):

    def __init__(self,
                 workflows = {}):
        #### Workflows ######
        self.WORKFLOW_RUNNING = False
        self.workflows = workflows
        self.workflow_executions = {}
        self.running_tasks = {}


    def get_ai_instructions(self):
      return ""
    

    def get_tool_instructions(self):
      return ""
 

    def start_workflow(self, input: dict):
        self.WORKFLOW_RUNNING = True
        # print("START_WORKFLOW INPUT:")
        # pprint.pprint(input)
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
        
        # print("START WORKFLOW OUTPUT:")
        # pprint.pprint(resp)
        return workflow, resp


    def start_task(self, input: dict):
        # print("START_TASK INPUT:")
        # pprint.pprint(input)
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

        # print("START_TASK: TASK STARTED")
        # pprint.pprint(task)
        return task

    # COMPLETES THE CURRENT TASK AND RETURNS THE NEXT TASK

    def get_next_task(self, input: dict):
        # print("get_next_task INPUT:")
        # pprint.pprint(input)
       
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
                # print(resp)
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
        
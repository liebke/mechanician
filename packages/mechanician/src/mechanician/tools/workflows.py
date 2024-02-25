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

    tool_instructions = [
        {
            "type": "function",
            "function": {
                "name": "start_workflow",
                "description": "Starts a workflow process, it requires the name of the workflow, workflow_name. The result will be a Task object containing instructions that you should follow and additional input that you can use to complete the task. The task object will contain the task_id, the task_name, task_instructions, and a conditions object. Evaluate each statement in the conditions object and create a corresponding `decisions` object with the same keys as the conditions object and boolean vlaues representing your responses to the statements in the conditions object.",
                "parameters": {
                "type": "object",
                "properties": {
                    "workflow_name": {
                    "type": "object",
                    "description": "This is the name of the workflow to start. It must be a valid workflow name."
                    },
                    "input": {
                    "type": "object",
                    "description": "This is the input to the workflow."
                    }
                },
                "required": ["workflow_name", "input"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_next_task",
                "description": "Completes a task associated with a workflow process, if the Task contained 'decisions', evaluate each decision in the list in order and use the 'decisions' field in the 'get_next_task' tool, passing the value of the 'then' field as in the input `next` input parameter for the first condition that evaluates True, otherwise return the value of the 'else' field. If the Task does not contain 'decisions', follow the instructions and return a 'result' to the 'get_next_task' tool.",
                "parameters": {
                "type": "object",
                "properties": {
                    "current_task_id": {
                    "type": "string",
                    "description": "This is the `task_id` of the current task that has been completed."
                    },
                    "result": {
                    "type": "object",
                    "description": "This is your result for the task to be completed."
                    },
                    "next": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "After evaluating the `next` parameter of the current task, you will have a list of the next tasks to complete, if any."
                    }
                },
                "required": ["current_task_id"]
                }
            }
        }
    ]

    ai_instructions = """# Workflow for AI

    You are an AI assistant with access to tools for performing different tasks. and can start workflow processes by name. After starting a workflow with the `start_workflow` tool, you will receive a task, once you have completed the instructions in the task, YOU MUST CALL the `get_next_task` tool, for EVERY SINGLE TASK you complete.

    The `next` field in the Task will contain a list of conditionals that you must evaluate, here is one example of the format you can expect:
    ```
    [{"if": "Is the value greater than $10 and less than $100?",
    "then": ["task2"]},
    {"elif": "Is the value less than $500?",
    "then": ["task4"]},
    {"else": ["task3"]}]
    ```

    But the conditional statements in the `next` can also be in natural language, like this:
    ```
    if the value is greater than $10 and less than $100
    then do task2
    else if the value is less than $500
    then do task4
    otherwise do task3
    ```

    * Evaluate each conditional and include the task list of the first conditional that you evaluate to be true as the `next` parameter of the `get_next_task` tool.

    * You MUST include the `task_id` of the current task in the `current_task_id` parameter of the `get_next_task` tool.

    * If the instructions say to include a result, then include the result in the `result` parameter of the `get_next_task` tool.

    * You will receive new tasks until all tasks are complete.
    """


    def __init__(self,
                 workflows = {}):
        #### Workflows ######
        self.WORKFLOW_RUNNING = False
        self.workflows = workflows
        self.workflow_executions = {}
        self.running_tasks = {}


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
        
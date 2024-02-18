from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector, OpenAIAssistantsConnector
from arango_memory.ltm_ai_tools import LTMAITools, run_workflow
from arango import ArangoClient
import os
import logging
from dotenv import load_dotenv
import traceback

logger = logging.getLogger(__name__)

###############################################################################
## INIT AI
###############################################################################

def init_ai(userid="test_user", 
            database_name="test_memory_db",
            workflows=None):
    arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
    ltm_tools = LTMAITools(arango_client=arango_client,
                           userid=userid,
                           database_name=database_name,
                           workflows=workflows)
    # Load current memories associated with userid
    memories = ltm_tools.recall_memories(userid)
    ai_instructions = ""
    with open("./instructions/ai_instructions.md", "r") as f:
        ai_instructions = f.read()
    # append userid to ai_instructions
    ai_instructions += f"\nuserid: {userid}\n"
    # append memories to ai_instructions
    ai_instructions += "memories:\n"
    ai_instructions += "\n".join(memories)


    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")

    if os.getenv("USE_OPENAI_ASSISTANTS_API", "False") == "True":
        ai_connector = OpenAIAssistantsConnector(api_key=api_key, model_name=model_name)
    else:
        ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)

    ai = TAGAI(ai_connector=ai_connector, 
               instruction_set_directory="./instructions",
               ai_instructions=ai_instructions,
               tools=ltm_tools,
               name="Long Term Memory-Enabled AI (LTMEAI)")
    
    return ai


###############################################################################
## Main program execution
###############################################################################

# Task Types: Task, Decision, Start, End
workflows = {"example_flow" : {
    "start": {"next": ["task1"]},
    "task1": {  
                "instructions": "Call the `get_weather` method, if you have called it before you still MUST call it again, you can pass it parameters with information you remember, or ask the user if you need additional information. Once you have completed the task, call get_next_task, and you will receive the next task to work on.",
                "next": ["decision1"]
            },
    "decision1": { 
                    "decisions": [{"if": "Is the temperature above 70F and below 75F?",
                                   "then": ["task2"]},
                                   {"elif": "Is the weather snowy or below 20F?",
                                    "then": ["task4"]},
                                   {"else": ["task3"]}],
                },
    "task2": {
                "instructions": "Tell the user a joke using the weather information.",
                # end the workflow by excluding the "next" key
            },
    "task3": {
                "instructions": "Write a limerick about the weather, and then call get_next_task and begin the next task.",
                # loop back to task1
                "next": ["task1"]
            },
    "task4": {
                "instructions": "Write a haiku using the weather information.",
                # end the workflow by excluding the "next" key
            },
    }
}

def main():
    DELETE_MEMORY_ON_EXIT = "False"
    ai = None
    try: 
        load_dotenv()
        database_name = "test_memory_db"
        userid = "test_user"
        ai = init_ai(userid=userid, database_name=database_name, workflows=workflows)
        # shell.run(ai)
        run_workflow(ai, "example_flow")

    except Exception as e:
        logger.error(e)
        traceback.print_exc()
    finally:
        if ai and ai.tools and ai.tools.doc_mgr:
            ai.save_tuning_session()
            if DELETE_MEMORY_ON_EXIT == "True":
                ai.tools.doc_mgr.delete_database(database_name)

if __name__ == '__main__':
    main()

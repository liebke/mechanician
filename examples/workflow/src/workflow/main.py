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
                    # "next": [{"if": "Is the temperature above 70F and below 75F?",
                    #           "then": ["task2"]},
                    #          {"elif": "Is the weather snowy or below 20F?",
                    #           "then": ["task4"]},
                    #          {"else": ["task3"]}],

                    "next": ["""if the temperature above 35F and below 75F 
                                then do task2 and task3 next
                                else if the weather snowy or below 20F
                                then do task4
                                otherwise do task3""",]
                },
    "task2": {
                "instructions": "Tell the user a joke using the weather information.",
                # end the workflow by excluding the "next" key
            },
    "task3": {
                "instructions": "Write a limerick about the weather, and then call get_next_task and begin the next task.",
                # end the workflow by excluding the "next" key
            },
    "task4": {
                "instructions": "Write a haiku using the weather information.",
                # loop back to task1
                "next": ["task1"]
            },
    },

    "puzzle_flow" : {
        "start": {"next": ["puzzle_description"]},
        "puzzle_description": {  
                    "instructions": "Ask the user to provide the puzzle to be solved. This can be a text-based logic puzzle, a mathematical puzzle, or any problem that requires logical deduction. Ensure you understand the puzzle's rules and objectives clearly before proceeding.",
                    "next": ["problem_analysis"]
                },
        "problem_analysis": { 
                    "instructions": "Analyze the puzzle's structure and identify the key elements involved. Determine what type of logical reasoning, mathematical concepts, or pattern recognition is required to solve the puzzle. This step may involve breaking down the puzzle into smaller, more manageable parts.",
                    "next": ["strategy_formulation"]
                },
        "strategy_formulation": {
                    "instructions": "Formulate a strategy for solving the puzzle. This could involve a step-by-step approach, using algorithms, applying elimination techniques, or constructing models to test different scenarios. Outline your planned approach clearly.",
                    "next": ["solution_execution"]
                },
        "solution_execution": {
                    "instructions": "Execute the strategy formulated in the previous step. This involves applying logical deductions, calculations, or iterative testing to arrive at the puzzle's solution. Keep track of your steps and reasoning for review.",
                    "next": ["review_and_optimization"]
                },
        "review_and_optimization": {
                    "instructions": "Review the solution process and the final answer. Verify the solution against the puzzle's rules and objectives. If the solution is incorrect or suboptimal, identify where adjustments can be made and refine your strategy accordingly.",
                    #End the workflow by excluding the "next" key
                }
    },

    "family_tree": {
    "start": {"next": ["initialize_tree"]},
    "initialize_tree": {  
                "instructions": "Start by initializing an empty graph structure to represent the family tree. Ask the user for the root individual (e.g., the oldest known ancestor) to create the first node.",
                "next": ["add_individual"]
            },
    "add_individual": { 
                "instructions": "Ask the user to input information about a new individual to add to the tree. This includes the person's name, and optionally, birthdate, and death date. Each individual should have a unique identifier.",
                "next": ["add_relationship"]
            },
    "add_relationship": {
                "instructions": "For the newly added individual, ask the user about any familial relationships that should be connected (e.g., parent, child). This step may involve selecting from existing individuals in the tree to create an edge.",
                "next": ["review_relationships"]
            },
    "review_relationships": {
                "instructions": "Review the added relationships for consistency and completeness. Check if the individual's parents are added; if not, loop back to 'add_individual' to add missing parents. Ensure there are no logical inconsistencies (e.g., a child older than a parent).",
                "next": ["decision_point"]
            },
    "decision_point": {
                "instructions": "Ask the user if they want to add another individual to the tree. If yes, loop back to 'add_individual'. If no, proceed to 'analyze_tree'.",
                "next": ["analyze_tree", "add_individual"]
            },
    "analyze_tree": {
                "instructions": "Analyze the constructed family tree for insights. This could involve identifying the largest generation, calculating the average lifespan (if dates are provided), or finding the individual with the most direct descendants.",
                "next": ["conclusion"]
            },
    "conclusion": {
                "instructions": "Provide a summary of the family tree analysis, highlighting interesting findings. Offer the user options to save/export the tree, add more details, or start a new tree.",
            }
}


}


import difflib
import json
from pprint import pprint

def get_best_match(dictionary, query):
    lower_case_dict = {k.lower(): v for k, v in dictionary.items()}
    words = query.lower().split()
    matches = []
    for word in words:
        matches.extend(difflib.get_close_matches(word, lower_case_dict.keys()))
    if matches:
        best_match = max(matches, key=matches.count)
        return lower_case_dict[best_match]
    else:
        return None

def weather_report(location):
    # open middle_earth_weather.json file
    with open("./middle_earth_weather.json", "r") as f:
        # use json to load the file
        weather_data = json.load(f)

    print("WEATHER DATA:")
    pprint(weather_data)

    return get_best_match(weather_data, location)

def weather_main():
    location = input("Please enter a location: ")
    weather = weather_report(location)
    print("\n\n")
    print(weather.get("report"))
    print("\n\n")

def main():
    DELETE_MEMORY_ON_EXIT = "False"
    ai = None
    try: 
        load_dotenv()
        database_name = "test_memory_db"
        userid = "test_user"
        ai = init_ai(userid=userid, database_name=database_name, workflows=workflows)
        shell.run(ai)
        # run_workflow(ai, "example_flow")

    except Exception as e:
        logger.error(e)
        traceback.print_exc()
    finally:
        if ai and ai.tools and ai.tools.doc_mgr:
            ai.save_tuning_session()
            if DELETE_MEMORY_ON_EXIT == "True":
                ai.tools.doc_mgr.delete_database(database_name)

if __name__ == '__main__':
    # main()
    weather_main()

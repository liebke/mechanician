from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector
from mechanician.tools.workflows import WorkflowAITools
import os
import logging
from dotenv import load_dotenv
import traceback

logger = logging.getLogger(__name__)

###############################################################################
## INIT AI
###############################################################################

def init_ai(workflows=None):

    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")
    ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)
    workflow_tools = WorkflowAITools(workflows=workflows)
    ai = TAGAI(ai_connector=ai_connector, 
               tools=workflow_tools,
               name="Workflow-Enabled AI")
    return ai


###############################################################################
## Main program execution
###############################################################################

workflows = {
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


def main():
    ai = None
    try: 
        load_dotenv()
        ai = init_ai(workflows=workflows)
        shell.run(ai)

    except Exception as e:
        logger.error(e)
        traceback.print_exc()
    finally:
        if ai and ai.tools and ai.tools.doc_mgr:
            ai.save_tuning_session()


if __name__ == '__main__':
    main()

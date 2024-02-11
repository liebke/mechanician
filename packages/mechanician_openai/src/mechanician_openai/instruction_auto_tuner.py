from mechanician import shell
from mechanician_openai import OpenAIChatConnector, OpenAIAssistantsConnector
from mechanician.instruction_tuning import instruction_auto_tuning_ai
import os
import logging
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

###############################################################################
## INIT AI
###############################################################################

def init_ai():
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")
    if os.getenv("USE_OPENAI_ASSISTANTS_API", "False") == "True":
        ai_connector = OpenAIAssistantsConnector(api_key=api_key, model_name=model_name)
    else:
        ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)

    tuner_ai = instruction_auto_tuning_ai(ai_connector=ai_connector,
                                          tuning_session_dir="./tuning_sessions",
                                          instructions_dir="./instructions")
    return tuner_ai


###############################################################################
## Main program execution
###############################################################################

def main():
    try: 
        load_dotenv()
        ai = init_ai()
        shell.run(ai)
        
    finally:
        pass

if __name__ == '__main__':
    main()

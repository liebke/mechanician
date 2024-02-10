from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector, OpenAIAssistantsConnector
from mechanician.training.instruction_auto_tuning import InstructionAutoTuning
import os
import logging
from dotenv import load_dotenv


logger = logging.getLogger(__name__)

###############################################################################
## INIT AI
###############################################################################

def init_tuner():
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")

    if os.getenv("USE_OPENAI_ASSISTANTS_API", "False") == "True":
        ai_connector = OpenAIAssistantsConnector(api_key=api_key, model_name=model_name)
    else:
        ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)
    iat = InstructionAutoTuning(training_data_dir="./test_results",
                                instructions_dir="./instructions")
    tuner_ai = iat.init_ai(ai_connector)
    return tuner_ai


###############################################################################
## Main program execution
###############################################################################

def main():
    try: 
        load_dotenv()
        ai = init_tuner()
        shell.run(ai)
        
    finally:
        pass

if __name__ == '__main__':
    main()

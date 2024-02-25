from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector
from notepad.example_ai_tools import ExampleAITools
from mechanician.tools.notepad import NotepadAITools, NotepadFileStore
import os
import logging
from dotenv import load_dotenv
import traceback

logger = logging.getLogger(__name__)

###############################################################################
## INIT AI
###############################################################################

def init_ai(notepad_name, notepad_directory_name="./notepads"):
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")
    ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)
    ex_tools = ExampleAITools()
    notepad_file_store = NotepadFileStore(notepad_name=notepad_name,
                                          notepad_directory_name=notepad_directory_name)
    notepad_tools = NotepadAITools(notepad_store=notepad_file_store)
    ai = TAGAI(ai_connector=ai_connector, 
               tools=[ex_tools, notepad_tools],
               name="Notepad-Enabled AI")
    return ai


###############################################################################
## Main program execution
###############################################################################

def main():
    DELETE_NOTEPAD_ON_EXIT = "False"
    ai = None
    try: 
        load_dotenv()
        notepad_name = "test_notepad"
        ai = init_ai(notepad_name=notepad_name)
        shell.run(ai)

    except Exception as e:
        logger.error(e)
        traceback.print_exc()
    finally:
        if ai and ai.tools:
            ai.save_tuning_session()
            if DELETE_NOTEPAD_ON_EXIT == "True":
                ai.tools.delete_notepad()

if __name__ == '__main__':
    main()

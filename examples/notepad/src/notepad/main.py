from mechanician import TAGAI, shell
from mechanician_openai import OpenAIChatConnector
# from mechanician_mistral.mistral_ai_connector import MistralAIConnector
from notepad.weather_ai_tools import MiddleEarthWeatherAITools
from mechanician.tools.notepads import NotepadAITools, NotepadFileStore
from mechanician_arangodb.notepad_store import ArangoNotepadStore
import os
import logging
from dotenv import load_dotenv
import traceback
import sys

from arango import ArangoClient

logger = logging.getLogger(__name__)

###############################################################################
## INIT AI
###############################################################################

def init_ai(notepad_name, notepad_directory_name="./notepads"):
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME")
    ai_connector = OpenAIChatConnector(api_key=api_key, model_name=model_name)
    # api_key = os.getenv("MISTRAL_API_KEY")
    # model_name = os.getenv("MISTRAL_MODEL_NAME")
    # ai_connector = MistralAIConnector(api_key=api_key, model_name=model_name)
    
    ex_tools = MiddleEarthWeatherAITools()
    notepad_file_store = NotepadFileStore(notepad_name=notepad_name,
                                          notepad_directory_name=notepad_directory_name)
    # ArangoDB notepad store
    database_name="test_notepad_db"
    notepad_collection_name="notepads"
    arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
    arango_notepad_store = ArangoNotepadStore(notepad_name=notepad_name,
                                              arango_client=arango_client, 
                                              database_name=database_name,
                                              notepad_collection_name=notepad_collection_name,
                                              db_username=os.getenv("ARANGO_USERNAME"),
                                              db_password=os.getenv("ARANGO_PASSWORD"))
    arango_notepad_tools = NotepadAITools(notepad_store=arango_notepad_store)
    # END ArangoDB notepad store

    notepad_tools = NotepadAITools(notepad_store=notepad_file_store)
    ai = TAGAI(ai_connector=ai_connector, 
            #    tools=[ex_tools, notepad_tools],
               tools=[ex_tools, arango_notepad_tools],
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
        notepad = "test_notepad"
        # sys.argv[0] is the script name itself
        for i in range(1, len(sys.argv)):
            if sys.argv[i] == "--notepad":
                notepad = sys.argv[i + 1]
 
        ai = init_ai(notepad_name=notepad)
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

from dotenv import load_dotenv
from pprint import pprint
from mechanician.tools import AITools, MechanicianToolsProvisioner
import logging
from mechanician_chroma.chroma_connector import ChromaConnector
import traceback

logger = logging.getLogger(__name__)

load_dotenv()

###############################################################################
## ChromaAIToolsProvisioner
###############################################################################
    
class ChromaAIToolsProvisioner(MechanicianToolsProvisioner):
        
        def __init__(self,
                     collection_name, 
                     data_path="./data/chromadb",
                     tool_instructions_file_name=None,
                     ai_instructions_file_name=None,
                     instruction_set_directory="./src/instructions"):
            self.collection_name = collection_name
            self.data_path = data_path
            self.tool_instructions_file_name = tool_instructions_file_name
            self.ai_instructions_file_name = ai_instructions_file_name
            self.instruction_set_directory = instruction_set_directory
    

        def create_tools(self, context: dict={}):
            # Use the context to control access to resources provided by the connector.
            # ...
            return ChromaAITools(collection_name=self.collection_name,
                                 data_path=self.data_path,
                                 tool_instructions_file_name=self.tool_instructions_file_name,
                                 ai_instructions_file_name=self.ai_instructions_file_name,
                                 instruction_set_directory=self.instruction_set_directory)


###############################################################################
## TMDbAITools
###############################################################################

class ChromaAITools(AITools):
    """AI Tools for interacting with the Chroma DB."""

    def __init__(self, 
                 collection_name, 
                 data_path="./data/chromadb",
                 tool_instructions=None,
                 tool_instructions_file_name=None,
                 ai_instructions_file_name=None,
                 instruction_set_directory=None):

                 self.collection_name = collection_name
                 self.data_path = data_path
                 self.chroma_connector = ChromaConnector(collection_name=self.collection_name,
                                                         data_path=self.data_path)
                 if tool_instructions is not None:
                    self.tool_instructions = tool_instructions
                
                 self.tool_instructions_file_name = tool_instructions_file_name
                 self.ai_instructions_file_name = ai_instructions_file_name
                 self.instruction_set_directory = instruction_set_directory
                 

    def query(self, params:dict):
        try:
            if self.chroma_connector.has_function("chroma_query"):
                response = self.chroma_connector.chroma_query(params)
                return response
            else:
                error_msg = f"Unknown function: chroma_query"
                logger.info(error_msg)
                return {"status": "error", "error_message": error_msg}
        
        except Exception as e:
            error_msg = f"Error calling function chroma_query: {e}"
            logger.error(error_msg)
            traceback.print_exc()
            return {"status": "error", "error_message": error_msg}

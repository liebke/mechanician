import json
from mechanician import TAGAI
from mechanician.ai_connectors import AIConnector
from mechanician.ai_tools import AITools
from mechanician.util import print_markdown
from rich.console import Console
import logging
import os
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

tuner_instructions = """
Your role is an Instructor AI that will evaluate the performance of an AI Assistant given its instructions,
the tool instructions it was provided, and a transcript of its interactions with a user.

You will be provided a JSON document containing tuning session data, it includes:

ai_instructions: Instructions provided to the AI describing it role
transcript: a transcript of the interaction between the ASSISTANT, the EVALUATOR, and the TOOLS the ASSISTANT used
tool_instructions: A description of each tool and its parameters
test_results: If any where available

Please identify any errors made by the Assistant, as revealed through feedback within the transcript or from tool outcomes. 
Also, highlight behaviors or responses that were useful or explicitly requested by the user.

Once you have completed your evaluation, use the 'draft_instructions' tool you have been provided to a CONSISE UPDATE to the existing 'ai_instructions'
that will prevent the errors you have identified while maintaining the intended role of the ASSISTANT.

BE SPECIFIC to the AI's role and the tools it uses when revising its instructions.


"""

###############################################################################
## INSTRUCTION AUTO TUNING AI
###############################################################################

def instruction_auto_tuning_ai(ai_connector: AIConnector,
                               tuning_session_dir="./tuning_sessions",
                               instructions_dir="./instructions"):
    
    tools = AutoTuningAITools(tuning_session_dir=tuning_session_dir,
                              instructions_dir=instructions_dir)
    
    ai = TAGAI(ai_connector=ai_connector, 
                ai_instructions=tuner_instructions, 
                tool_instructions=auto_tuner_tool_instructions,
                tools=tools,
                name="Instruction Auto-Tuner AI")
    return ai


###############################################################################
# AutoTuningAITools
###############################################################################

class AutoTuningAITools(AITools):

    def __init__(self, 
                 tuning_session_dir=None,
                 instructions_dir=None):
        self.revised_instructions = None
        self.tuning_session_dir = tuning_session_dir
        self.instructions_dir = instructions_dir
        self.instructions_file_name = "instructions.json"
        self.tuning_session_file_name = "tuning_session.json"
        self.draft_instructions_file_name = f"draft_{self.instructions_file_name}"
        self.instructions_file_path = os.path.join(self.instructions_dir, self.instructions_file_name)
        self.draft_instructions_file_path = os.path.join(self.instructions_dir, self.draft_instructions_file_name)
        self.tuning_session_file_path = os.path.join(self.tuning_session_dir, self.tuning_session_file_name)
        self.tuning_session = None

        # ensure the directories exist and set them up if they don't
        if self.tuning_session_dir is not None:
            os.makedirs(self.tuning_session_dir, exist_ok=True)
        if self.instructions_dir is not None:
            os.makedirs(self.instructions_dir, exist_ok=True)

        # load the existing instructions if they exist.
        if os.path.exists(self.instructions_file_path):
            with open(self.instructions_file_path, 'r') as f:
                self.instructions = json.load(f)
        else:
            self.instructions = {"tool_instructions": [],
                                 "ai_instructions": "EMPTY"}

        # load the tuning session if it exists
        if os.path.exists(self.tuning_session_file_path):
            with open(self.tuning_session_file_path, 'r') as f:
                self.tuning_session = json.load(f)

        # If the tool_instructions is [], set them to the 'tool_instruction' field of the tuning_session object.
        if not self.instructions.get("tool_instructions") and self.tuning_session is not None:
            self.instructions["tool_instructions"] = self.tuning_session.get("tool_instructions")


    def draft_ai_instructions(self, input):
        try:
            self.revised_instructions = input.get("revised_instructions")
            if self.revised_instructions is None:
                resp = "revised_instructions parameter is required"
                logger.info(resp)
                return resp
            console = Console()
            print_markdown(console, "# REVISED INSTRUCTIONS:")
            print_markdown(console, f"{self.revised_instructions}")
            # Write out the revised instructions to the instructions file
            self.instructions["ai_instructions"] = self.revised_instructions
            with open(os.path.join(self.instructions_dir, self.draft_instructions_file_name), 'w') as f:
                json.dump(self.instructions, f, indent=2)
            resp = "Instructions revised successfully"
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def draft_tool_instructions(self, input):
        try:
            tool_name = input.get("tool_name")
            revised_tool_instructions = input.get("revised_tool_instructions")
            if revised_tool_instructions is None or tool_name is None:
                resp = "revised_tool_instructions and tool_name parameters are required"
                logger.info(resp)
                return resp
            console = Console()
            print_markdown(console, f"# REVISED TOOL INSTRUCTIONS FOR {tool_name}:")
            print_markdown(console, f"{revised_tool_instructions}")
            # write out the revised tool instructions to the correct tool in the tool_instructions list
            for tool in self.instructions["tool_instructions"]:
                if tool.get("function").get("name") == tool_name:
                    tool["function"]["description"] = revised_tool_instructions
                    break
            with open(os.path.join(self.instructions_dir, self.draft_instructions_file_name), 'w') as f:
                logger.debug("Revised Tool Instructions:")
                logger.debug(self.instructions)
                json.dump(self.instructions, f, indent=2)

            resp = "Tool instructions revised successfully"
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def draft_tool_parameter_instructions(self, input):
        try:
            tool_name = input.get("tool_name")
            parameter_name = input.get("parameter_name")
            revised_parameter_instructions = input.get("revised_parameter_instructions")
            if revised_parameter_instructions is None or tool_name is None or parameter_name is None:
                resp = "revised_parameter_instructions, tool_name, and parameter_name parameters are required"
                logger.info(resp)
                return resp
            console = Console()
            print_markdown(console, f"# REVISED TOOL PARAMETER INSTRUCTIONS FOR {tool_name}/{parameter_name}:")
            print_markdown(console, f"{revised_parameter_instructions}")
            # write out the revised tool parameter instructions to the correct tool in the tool_instructions list
            for tool in self.instructions["tool_instructions"]:
                if tool.get("function").get("name") == tool_name:
                    for parameter in tool.get("function").get("parameters").get("properties"):
                        if parameter == parameter_name:
                            tool["function"]["parameters"]["properties"][parameter]["description"] = revised_parameter_instructions
                            break
                    break
            with open(os.path.join(self.instructions_dir, self.draft_instructions_file_name), 'w') as f:
                logger.debug("Revised Tool Parameter Instructions:")
                logger.debug(self.instructions)
                json.dump(self.instructions, f, indent=2)

            resp = "Tool instructions revised successfully"
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"


    def commit_draft_instructions(self, input):
        try:
            if os.path.exists(self.draft_instructions_file_path):
              # If previous version of instruction file exists
              if os.path.exists(self.instructions_file_path):
                # Create archives directory if it doesn't exist
                archive_dir = os.path.join(self.instructions_dir, "archives")
                os.makedirs(archive_dir, exist_ok=True)
                # Get the current timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                # Get the original name of the old file without the extension
                original_name = os.path.basename(os.path.splitext('./instructions/instructions.json')[0])
                # Specify the new directory and new name
                new_name = os.path.join(archive_dir, f"{original_name}_{timestamp}.json")
                # Rename the old file, moving into the archives directory
                os.rename(self.instructions_file_path, new_name)
              
              # Rename the new file
              os.rename(self.draft_instructions_file_path, self.instructions_file_path)

            else:
                resp = "Draft instructions file not found"
                logger.info(resp)
                return resp

            resp = "Draft Instructions saved successfully"
            logger.info(resp)
            return resp
        
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"

    

###############################################################################
# Auto Tuner Tool Instructions
###############################################################################
auto_tuner_tool_instructions = [
    {
      "type": "function",
      "function": {
        "name": "draft_ai_instructions",
        "description": "Revises an AI's system instructions.",
        "parameters": {
          "type": "object",
          "properties": {
            "revised_instructions": {
              "type": "string",
              "description": "The revised instructions for the AI."
            }
          },
          "required": ["revised_instructions"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "draft_tool_instructions",
        "description": "Revises Tool instructions.",
        "parameters": {
          "type": "object",
          "properties": {
            "revised_tool_instructions": {
              "type": "string",
              "description": "The revised instructions for the tool."
            },
            "tool_name": {
              "type": "string",
              "description": "The name of the tool to have its instructions revised."
            }
          },
          "required": ["tool_name", "revised_tool_instructions"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "draft_tool_parameter_instructions",
        "description": "Revises the parameter instructions for a tool.",
        "parameters": {
          "type": "object",
          "properties": {
            "revised_parameter_instructions": {
              "type": "string",
              "description": "The revised tool parameter instructions for the assistant."
            },
            "parameter_name": {
              "type": "string",
              "description": "The name of the parameter to have its instructions revised."
            },
            "tool_name": {
              "type": "string",
              "description": "The name of the tool's whose parameter will have its instructions revised."
            }
          },
          "required": ["parameter_name", "tool_name", "revised_parameter_instructions"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "commit_draft_instructions",
        "description": "Commits the draft of the new instructions, replacing the original instructions after making an archive copy of the original instructions.",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    },
  ]

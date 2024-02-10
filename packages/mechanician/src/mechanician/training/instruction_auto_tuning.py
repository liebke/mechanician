import json
# import yaml
from pprint import pprint
from mechanician import TAGAI
from mechanician.ai_connectors import AIConnector
from mechanician.ai_tools import AITools
from mechanician.util import print_markdown
from rich.console import Console
import logging
import os

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# logger.addHandler(handler)

tuner_instructions = """
Your role is an Instructor AI that will evaluate the performance of an AI Assistant given its instructions,
the tool instructions it was provided, and a transcript of its interactions with a user.

You will be provided a JSON document containing training session data, it includes:

ai_instructions: Instructions provided to the AI describing it role
transcript: a transcript of the interaction between the ASSISTANT, the EVALUATOR, and the TOOLS the ASSISTANT used
tool_instructions: A description of each tool and its parameters
test_results: If any where available

Please identify any errors made by the Assistant, as revealed through feedback within the transcript or from tool outcomes. 
Also, highlight behaviors or responses that were useful or explicitly requested by the user.

Once you have completed your evaluation, use the 'revise_instructions' tool you have been provided to a CONSISE UPDATE to the existing 'ai_instructions'
that will prevent the errors you have identified while maintaining the intended role of the ASSISTANT.

BE SPECIFIC to the AI's role and the tools it uses when revising its instructions.


"""

class InstructionAutoTuning():

    def __init__(self, 
                 training_data_dir=None,
                 instructions_dir=None):
        self.ai_connector = None
        self.tuner_instructions = tuner_instructions
        self.tool_instructions = auto_tuner_tool_instructions
        self.tools = AutoTuningAITools(training_data_dir=training_data_dir,
                                       instructions_dir=instructions_dir)
        self.ai = None
        self.name = "Instruction Auto-Tuning: Instructor AI"


    ###############################################################################
    ## INIT AI
    ###############################################################################

    def init_ai(self, ai_connector: AIConnector):
        self.ai_connector = ai_connector
        self.ai = TAGAI(ai_connector=self.ai_connector, 
                        ai_instructions=self.tuner_instructions, 
                        tool_instructions=self.tool_instructions,
                        tools=self.tools,
                        name=self.name)
        return self.ai


    def get_training_session_data(self, ai: TAGAI):
        training_session_data = {}
        training_session_data["tool_instructions"] = ai.tool_instructions
        training_session_data["ai_instructions"] = ai.ai_instructions
        training_session_data["transcript"] = ai.get_message_history()
        training_session_data["test_results"] = None
        return json.dumps(training_session_data, indent=2)
    

    def write_training_session_data(self, ai: TAGAI, file_path):
        with open(file_path, 'w') as f:
            f.write(self.get_training_session_data(ai))


    def read_training_session_data(self, file_path):
        with open(file_path, 'r') as f:
            return json.loads(f)


    def get_iat_prompt(self, training_session_path): 
        instructions = self.tuner_instructions
        transcript = self.read_training_session_data(training_session_path)
        training_session_data = {"ai_instructions": transcript.get("ai_instructions"),
                                "tool_instructions": transcript.get("tool_instructions"),
                                "transcript": transcript.get("transcript"),
                                "test_results": transcript.get("test_results")}
        
        resp = f"""
        {instructions}

        ------------------
        [TRAINING SESSION DATA]
        {training_session_data}
        [END TRAINING SESSION DATA]
        """
        return resp


    def write_iat_prompt(self, training_session_data_path, output_file_path):
        with open(output_file_path, 'w') as f:
            f.write(self.get_iat_prompt(training_session_data_path))



###############################################################################
# AutoTuningAITools
###############################################################################

class AutoTuningAITools(AITools):

    def __init__(self, 
                 training_data_dir=None,
                 instructions_dir=None):
        self.revised_instructions = None
        self.training_data_dir = training_data_dir
        self.instructions_dir = instructions_dir
        self.instructions_file_name = "instructions.json"
        self.training_data_file_name = "training_session.json"

        # ensure the directories exist and set them up if they don't
        if self.training_data_dir is not None:
            os.makedirs(self.training_data_dir, exist_ok=True)
        if self.instructions_dir is not None:
            os.makedirs(self.instructions_dir, exist_ok=True)

        # load the instructions if they exist.
        instructions_file_path = os.path.join(self.instructions_dir, self.instructions_file_name)
        if os.path.exists(instructions_file_path):
            with open(instructions_file_path, 'r') as f:
                self.instructions = json.load(f)
        else:
            self.instructions = {"tool_instructions": [],
                                 "ai_instructions": "EMPTY"}

        # load the training data if it exists
        training_data_file_path = os.path.join(self.training_data_dir, self.training_data_file_name)
        if os.path.exists(training_data_file_path):
            with open(training_data_file_path, 'r') as f:
                self.training_data = json.load(f)

        # If the tool_instructions is [], set them to the 'tool_instruction' field of the training_data object.
        if not self.instructions.get("tool_instructions") and self.training_data is not None:
            self.instructions["tool_instructions"] = self.training_data.get("tool_instructions")


    def revise_ai_instructions(self, input):
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
            with open(os.path.join(self.instructions_dir, self.instructions_file_name), 'w') as f:
                json.dump(self.instructions, f, indent=2)
            resp = "Instructions revised successfully"
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def revise_tool_instructions(self, input):
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
            with open(os.path.join(self.instructions_dir, self.instructions_file_name), 'w') as f:
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
        

    def revise_tool_parameter_instructions(self, input):
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
            with open(os.path.join(self.instructions_dir, self.instructions_file_name), 'w') as f:
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

    

    

###############################################################################
# Auto Tuner Tool Instructions
###############################################################################
auto_tuner_tool_instructions = [
    {
      "type": "function",
      "function": {
        "name": "revise_ai_instructions",
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
        "name": "revise_tool_instructions",
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
        "name": "revise_tool_parameter_instructions",
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
  ]

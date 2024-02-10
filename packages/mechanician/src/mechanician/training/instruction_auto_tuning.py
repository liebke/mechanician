import json
import yaml
from pprint import pprint
from mechanician.ai_connectors import AIConnector

iat_instructions = """
Below is training session data recording during the interactive session between a EVALUATOR AI and an AI ASSISTANT, it includes:

ai_instructions: Instructions provided to the AI describing it role
transcript: a transcript of the interaction between the ASSISTANT, the EVALUATOR, and the TOOLS the ASSISTANT used
tool_instructions: A description of each tool and its parameters
test_results: If any where available

Please identify any errors made by the Assistant, as revealed through feedback within the transcript or from tool outcomes. 
Also, highlight behaviors or responses that were useful or explicitly requested by the user.

"""

iat_instructions_v2 = """
Below is training session data recording during the interactive session between a EVALUATOR AI and an AI ASSISTANT, it includes:

ai_instructions: Instructions provided to the AI describing it role
transcript: a transcript of the interaction between the ASSISTANT, the EVALUATOR, and the TOOLS the ASSISTANT used
tool_instructions: A description of each tool and its parameters
test_results: If any where available

Your task is to refine and improve the instructions for the ASSISTANT based on an analysis of a 
provided interaction transcript, original system instructions, and tool instructions. 

Identify any errors made by the Assistant, as revealed through feedback within the transcript or 
from tool outcomes. 

Also, highlight behaviors or responses that were useful or explicitly requested by the user. 

Use these insights to create enhanced instructions that clearly articulate how the Assistant 
should address identified issues, incorporate user preferences, and replicate successful strategies. 

Provide the revised instructions in a structured, clear format with examples where applicable.

Please provide revised and improved ai_instructions to the AI so that it can 
perform its role better, please start your response with "[ai_instructions]", only include 
the revised instructions and no other comments, and when complete end with "[end ai_instructions]" 
and no other words.
"""

iat_instructions_v1 = """
Below is training session data recording during the interactive session between a EVALUATOR AI and an AI ASSISTANT, it includes:

ai_instructions: Instructions provided to the AI describing it role
transcript: a transcript of the interaction between the ASSISTANT, the EVALUATOR, and the TOOLS the ASSISTANT used
tool_instructions: A description of each tool and its parameters
test_results: If any where available

1. I would like you to evaluate the ASSISTANT AI's performance based on the instructions it was provided using the training transcript.

2. I would like you to evaluate the quality of the tool descriptions and the tool responses from the transcript.

3. I would like you to evaluate the EVALUATOR AI's performance based on its interactions with the ASSISTANT using the transcript.

4. I would like you to improve the tool descriptions and suggest if the output of each tool can be improved.

5. Lastly, I would like you to provide revised and improved ai_instructions to the AI so that it can perform its role better, please start your response with "[ai_instructions]",
  only include the revised instructions and no other comments, and when complete end with "[end ai_instructions]" and no other words.

"""


class InstructionAutoTuning():

    def __init__(self, ai_connector: AIConnector):
        self.ai_connector = ai_connector
        self.iat_instructions = iat_instructions



    # def get_tool_descriptions(self):
    #     tool_instructions = self.ai.tool_instructions
    #     func_descriptions = []
    #     for tool_schema in tool_instructions:
    #         func = tool_schema.get("function")
    #         params_desc = [
    #             {"name": name, "description": details["description"]}
    #             for name, details in func.get("parameters", {}).get("properties", {}).items()
    #         ]
    #         func_desc = {
    #             "name": func.get("name"),
    #             "description": func.get("description"),
    #             "parameters": params_desc
    #         }
    #         func_descriptions.append(func_desc)
        
    #     # resp = json.dumps(func_descriptions, indent=2)
    #     resp = yaml.dump(func_descriptions, default_flow_style=False)   
    #     return resp
    
    # def get_training_transcript(self):
    #     transcript = []
    #     messages = self.ai.get_messages()
    #     for message in messages:
    #         role = message.get("role")
    #         if role == "assistant":
    #             if message.get("tool_calls"):
    #                 transcript.append(f"ASSISTANT TOOL CALLS: {message.get('tool_calls')}")

    #             transcript.append(f"ASSISTANT: {message.get('content')}")
    #         elif role == "user":
    #             transcript.append(f"USER: {message.get('content')}")
    #         elif role == "tool":
    #             transcript.append(f"TOOL: {message.get('name')} ({message.get('tool_call_id')}) {message.get('content')}")
    #         elif role == "system":
    #             transcript.append(f"SYSTEM: {message.get('content')}")
    #         else:
    #             content = message.get("content")
    #             transcript.append(f"{role}: {content}")

    #     return transcript
    
    
    def get_training_session_data(self):
        training_session_data = {}
        training_session_data["tool_instructions"] = self.ai_connector.tool_instructions
        training_session_data["ai_instructions"] = self.ai_connector.ai_instructions
        training_session_data["transcript"] = self.ai_connector.get_message_history()
        training_session_data["test_results"] = None
        return json.dumps(training_session_data, indent=2)
    

    def write_training_session_data(self, file_path):
        with open(file_path, 'w') as f:
            f.write(self.get_training_session_data())

    def read_training_session_data(self, file_path):
        with open(file_path, 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)


    def get_iat_prompt(self, training_session_path): 
        instructions = self.iat_instructions
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


    def revise_instructions(self, revised_instructions):
        self.ai_connector.instructions = revised_instructions
        return self.ai_connector.instructions
    

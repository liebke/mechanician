from abc import ABC, abstractmethod
from typing import List, Dict
import os
import json
from datetime import datetime
import re


###############################################################################
## UserDataStore
###############################################################################

class UserDataStore(ABC):
    
    @abstractmethod
    def get_conversation_history(self, username: str, ai_name: str, conversation_id: str) -> List[Dict]:
        """
        Abstract method to get the conversation history for a given username, AI name, and conversation ID.
        """
        pass
    
    @abstractmethod
    def set_conversation_history(self, username: str, ai_name: str, conversation_id: str, message_history: List[Dict]):
        """
        Abstract method to set the conversation history for a given username, AI name, and conversation ID.
        """
        pass

    @abstractmethod
    def append_message_to_conversation(self, username: str, ai_name: str, conversation_id: str, message: Dict):
        """
        Abstract method to append a message to the conversation history for a given username, AI name, and conversation ID.
        """
        pass
    
    @abstractmethod
    def new_conversation(self, username: str, ai_name: str, conversation_id:str=None) -> str:
        """
        Abstract method to start a new conversation, returning a new conversation ID.
        """
        pass
    
    @abstractmethod
    def get_ai_instructions(self, username: str, ai_name: str) -> str:
        """
        Abstract method to get AI instructions for a given username and AI name.
        """
        pass
    
    @abstractmethod
    def set_ai_instructions(self, username: str, ai_name: str, ai_instructions: str):
        """
        Abstract method to set AI instructions for a given username and AI name.
        """
        pass
    
    @abstractmethod
    def get_ai_tool_instructions(self, username: str, ai_name: str) -> List[Dict]:
        """
        Abstract method to get AI tool instructions for a given username and AI name.
        """
        pass
    
    @abstractmethod
    def set_ai_tool_instructions(self, username: str, ai_name: str, ai_tool_instructions: List[Dict]):
        """
        Abstract method to set AI tool instructions for a given username and AI name.
        """
        pass


###############################################################################
## UserDataFileStore
###############################################################################

class UserDataFileStore(UserDataStore):

    def __init__(self, data_dir: str = "./data"):
        self.DATA_DIR = data_dir


    def _ensure_dir(self, path: str):
        """
        Ensure that the directories exist for the given path.
        """
        os.makedirs(path, exist_ok=True)


    def _get_conversation_file_path(self, username: str, ai_name: str, conversation_id: str) -> str:
        return os.path.join(self.DATA_DIR, f"users/{username}/conversations/{self.sanitize_for_filename(ai_name)}/{conversation_id}.json")


    def _get_ai_instructions_path(self, username: str, ai_name: str) -> str:
        return os.path.join(self.DATA_DIR, f"users/{username}/instructions/{self.sanitize_for_filename(ai_name)}/ai_instructions.md")


    def _get_ai_tool_instructions_path(self, username: str, ai_name: str) -> str:
        return os.path.join(self.DATA_DIR, f"users/{username}/instructions/{self.sanitize_for_filename(ai_name)}/ai_tool_instructions.json")


    def _get_conversation_file_path(self, username: str, ai_name: str, conversation_id: str) -> str:
        return os.path.join(self.DATA_DIR, f"users/{username}/conversations/{self.sanitize_for_filename(ai_name)}/{conversation_id}.jsonl")


    def get_conversation_history(self, username: str, ai_name: str, conversation_id: str) -> List[Dict]:
        file_path = self._get_conversation_file_path(username, ai_name, conversation_id)
        conversation_history = []
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    conversation_history.append(json.loads(line.strip()))
        except FileNotFoundError:
            return []
        return conversation_history


    def set_conversation_history(self, username: str, ai_name: str, conversation_id: str, message_history: List[Dict]):
        file_path = self._get_conversation_file_path(username, ai_name, conversation_id)
        self._ensure_dir(os.path.dirname(file_path))
        with open(file_path, "w", encoding="utf-8") as file:
            for message in message_history:
                file.write(json.dumps(message, ensure_ascii=False) + "\n")


    def new_conversation(self, username: str, ai_name: str, conversation_id=None) -> str:
        if conversation_id is None and conversation_id != "":
            conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
        self.set_conversation_history(username, ai_name, conversation_id, [])
        return conversation_id
    

    def get_most_recent_conversation_id(self, username: str, ai_name: str) -> str:
        """
        Retrieves the ID of the most recent conversation for a given username and AI name.
        
        :param username: The username to look up.
        :param ai_name: The AI name to look up.
        :return: The ID of the most recent conversation, or an empty string if there are no conversations.
        """
        sanitized_ai_name = self.sanitize_for_filename(ai_name)
        conversations_dir = os.path.join(self.DATA_DIR, f"users/{username}/conversations/{sanitized_ai_name}")
        
        try:
            # List all conversation files and sort them, assuming filenames are sortable (e.g., based on timestamp)
            conversations = sorted(os.listdir(conversations_dir))
            if conversations:
                # Assuming the file format is '<conversation_id>.jsonl', split to get the ID
                most_recent_conversation_file = conversations[-1]
                return most_recent_conversation_file.split('.')[0]
        except FileNotFoundError:
            # If the directory doesn't exist, there are no conversations for this AI
            pass
        
        return None  # Return an empty string if no conversations are found or the directory doesn't exist


    def list_conversations(self, username: str, ai_name: str) -> List[str]:
        """
        Returns a list of conversation IDs for a given username and AI name, 
        sorted to have the most recent conversations at the top.

        :param username: The username to look up.
        :param ai_name: The AI name to look up.
        :return: A list of conversation IDs, with the most recent at the top.
        """
        sanitized_ai_name = self.sanitize_for_filename(ai_name)
        conversations_dir = os.path.join(self.DATA_DIR, f"users/{username}/conversations/{sanitized_ai_name}")

        try:
            # List all conversation files and sort them in reverse to have the most recent first
            conversations_files = sorted(os.listdir(conversations_dir), reverse=True)
            # Extract the conversation ID from each filename assuming the format '<conversation_id>.jsonl'
            conversation_ids = [file.split('.')[0] for file in conversations_files]
            return [{"conversation_id": conv_id, "timestamp": self._convert_to_date_format(conv_id)} for conv_id in conversation_ids]

        except FileNotFoundError:
            # If the directory doesn't exist, there are no conversations for this AI
            return []
        

    def append_message_to_conversation(self, username: str, ai_name: str, conversation_id: str, message: Dict):
        file_path = self._get_conversation_file_path(username, ai_name, conversation_id)
        self._ensure_dir(os.path.dirname(file_path))
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(json.dumps(message, ensure_ascii=False) + "\n")


    def get_ai_instructions(self, username: str, ai_name: str) -> str:
        file_path = self._get_ai_instructions_path(username, ai_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            return ""


    def set_ai_instructions(self, username: str, ai_name: str, ai_instructions: str):
        file_path = self._get_ai_instructions_path(username, ai_name)
        self._ensure_dir(os.path.dirname(file_path))
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(ai_instructions)


    def get_ai_tool_instructions(self, username: str, ai_name: str) -> List[Dict]:
        file_path = self._get_ai_tool_instructions_path(username, ai_name)
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return []


    def set_ai_tool_instructions(self, username: str, ai_name: str, ai_tool_instructions: List[Dict]):
        file_path = self._get_ai_tool_instructions_path(username, ai_name)
        self._ensure_dir(os.path.dirname(file_path))
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(ai_tool_instructions, file, ensure_ascii=False, indent=4)




    def sanitize_for_filename(self, text: str, max_length: int = 255) -> str:
        """
        Converts a given string into a sanitized version suitable for filenames.
        
        :param text: The input string to sanitize.
        :param max_length: Maximum length of the filename. Defaults to 255, which is the typical maximum for most filesystems.
        :return: A sanitized string suitable for use as a filename.
        """
        # Lowercase the string
        sanitized = text.lower()
        
        # Replace spaces and unwanted characters
        sanitized = re.sub(r'\s+', '_', sanitized)  # Replace one or more spaces with underscore
        sanitized = re.sub(r'[\/\\:*?"<>|]', '', sanitized)  # Remove problematic characters
        
        # Truncate to max_length to avoid issues with long filenames
        return sanitized[:max_length]


    def _convert_to_date_format(self, date_str: str) -> str:
        """
        Convert a date string from "YYYYMMDDHHMMSS" format to "DD Month YYYY h:MMpm <System Timezone>" format.

        :param date_str: A date string in "YYYYMMDDHHMMSS" format.
        :return: A string representing the date in "DD Month YYYY h:MMpm <System Timezone>" format.
        """
        # Parse the input string into a datetime object
        dt = datetime.strptime(date_str, "%Y%m%d%H%M%S")

        # Get the current system timezone
        current_tz = datetime.now().astimezone().tzinfo

        # Convert the datetime object to the desired format with system timezone
        formatted_date = dt.astimezone(current_tz).strftime("%d %B %Y %-I:%M%p").lower()

        return formatted_date

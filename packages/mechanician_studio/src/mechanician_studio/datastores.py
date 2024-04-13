from abc import ABC, abstractmethod
from typing import List, Dict
import os
import json
from datetime import datetime
import re
import logging
from fastapi import File
import aiofiles
# import asyncio
from pprint import pprint

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


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
    def delete_conversation(self, username: str, ai_name: str, conversation_id: str) -> bool:
        """
        Abstract method to delete a conversation.
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

    @abstractmethod
    async def add_resource_file(self, username: str, ai_name: str, conversation_id: str, file: File, attributes: Dict = None):
        """
        Abstract method to add a resource file for a given username and AI name.
        """
        pass


###############################################################################
## UserDataFileStore
###############################################################################

class UserDataFileStore(UserDataStore):

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir


    def _ensure_dir(self, path: str):
        """
        Ensure that the directories exist for the given path.
        """
        os.makedirs(path, exist_ok=True)


    def _get_conversation_file_path(self, username: str, ai_name: str, conversation_id: str) -> str:
        return os.path.join(self.data_dir, f"users/{username}/conversations/{self.sanitize_for_filename(ai_name)}/{conversation_id}.json")


    def _get_ai_instructions_path(self, username: str, ai_name: str) -> str:
        return os.path.join(self.data_dir, f"users/{username}/instructions/{self.sanitize_for_filename(ai_name)}/ai_instructions.md")


    def _get_ai_tool_instructions_path(self, username: str, ai_name: str) -> str:
        return os.path.join(self.data_dir, f"users/{username}/instructions/{self.sanitize_for_filename(ai_name)}/ai_tool_instructions.json")


    def _get_conversation_file_path(self, username: str, ai_name: str, conversation_id: str) -> str:
        return os.path.join(self.data_dir, f"users/{username}/conversations/{self.sanitize_for_filename(ai_name)}/{conversation_id}.jsonl")


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
        if conversation_id is None or conversation_id != "":
            conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
            
        # Clear empty conversations before creating a new one
        self.clear_empty_conversations(username, ai_name)
        self.set_conversation_history(username, ai_name, conversation_id, [])
        return conversation_id
    

    def clear_empty_conversations(self, username: str, ai_name: str):
        logger.info("Clearing empty conversations")
        conversations_dir = os.path.join(self.data_dir, f"users/{username}/conversations/{self.sanitize_for_filename(ai_name)}")
        try:
            for filename in os.listdir(conversations_dir):
                file_path = os.path.join(conversations_dir, filename)
                with open(file_path, "r", encoding="utf-8") as file:
                    # Initialize a flag to indicate the presence of user messages
                    has_user_messages = False

                    # Attempt to read each line (message) in the file
                    for line in file:
                        try:
                            message = json.loads(line.strip())
                            # Check if the message is from a user
                            if message.get("role") == "user":
                                has_user_messages = True
                                break  # Stop reading further as we found a user message
                        except json.JSONDecodeError:
                            # Handle lines that do not contain valid JSON
                            continue
                    
                    # If no user messages were found, delete the conversation file
                    if not has_user_messages:
                        logger.info(f"Deleting conversation file without user messages: {file_path}")
                        os.remove(file_path)

        except FileNotFoundError:
            # Handle the case where the conversations directory does not exist
            logger.error("No conversations directory found.")


        
        

    def delete_conversation(self, username: str, ai_name: str, conversation_id: str) -> bool:
        """
        Deletes the specified conversation file for a given username, AI name, and conversation ID.
        
        :param username: Username of the conversation owner.
        :param ai_name: AI name associated with the conversation.
        :param conversation_id: ID of the conversation to delete.
        :return: True if the file was successfully deleted, False otherwise.
        """
        file_path = self._get_conversation_file_path(username, ai_name, conversation_id)
        try:
            # Check if the file exists before attempting to delete
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            else:
                logger.info(f"No file exists for conversation ID {conversation_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting conversation file: {e}")
            return False
        

    def get_most_recent_conversation_id(self, username: str, ai_name: str) -> str:
        """
        Retrieves the ID of the most recent conversation for a given username and AI name.
        
        :param username: The username to look up.
        :param ai_name: The AI name to look up.
        :return: The ID of the most recent conversation, or an empty string if there are no conversations.
        """
        sanitized_ai_name = self.sanitize_for_filename(ai_name)
        conversations_dir = os.path.join(self.data_dir, f"users/{username}/conversations/{sanitized_ai_name}")
        
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

        
    def list_conversations(self, username: str, ai_name: str) -> List[Dict[str, str]]:
        """
        Returns a list of conversation IDs and the first user message for a given username and AI name,
        sorted to have the most recent conversations at the top.

        :param username: The username to look up.
        :param ai_name: The AI name to look up.
        :return: A list of dictionaries, each with conversation_id, timestamp, and description (first user message).
        """
        sanitized_ai_name = self.sanitize_for_filename(ai_name)
        conversations_dir = os.path.join(self.data_dir, f"users/{username}/conversations/{sanitized_ai_name}")

        conversation_details = []

        try:
            # List all conversation files and sort them in reverse to have the most recent first
            conversations_files = sorted(os.listdir(conversations_dir), reverse=True)

            for file_name in conversations_files:
                conversation_id = file_name.split('.')[0]
                file_path = os.path.join(conversations_dir, file_name)
                description = self._get_first_user_message(file_path)
                
                conversation_details.append({
                    "conversation_id": conversation_id,
                    "ai_name": ai_name,
                    "username": username,
                    "timestamp": self._convert_to_date_format(conversation_id),
                    "description": description
                })

        except FileNotFoundError:
            # If the directory doesn't exist, there are no conversations for this AI
            return []

        return conversation_details

    def _get_first_user_message(self, file_path: str) -> str:
        """
        Extracts the "content" of the first message by a user from a .jsonl file.

        :param file_path: Path to the conversation file.
        :return: The content of the first user message, or an empty string if not found.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                message = json.loads(line.strip())
                if message.get("role") == "user":
                    return message.get("content", "")
        return ""  # Return an empty string if no user message is found
    

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
    

    async def add_resource_file(self, username: str, ai_name: str, conversation_id: str, file: File, attributes: Dict = {}):
        """
        A method to add or update a resource file for a given username and AI name.
        """
        resource_dir = os.path.join(self.data_dir, "users", username, "resources")
        resource_data_dir = os.path.join(resource_dir, "data")
        file_path = os.path.join(resource_data_dir, file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write the file to the directory asynchronously, overwriting existing file
        async with aiofiles.open(file_path, "wb") as buffer:
            while True:
                data = await file.read(1024)
                if not data:
                    break
                await buffer.write(data)

        # Prepare the resource entry
        resource_entry = {
            "file_path": file_path,
            "filename": file.filename,
            "file_type": file.content_type,
            "file_extension": os.path.splitext(file.filename)[1],
            "ai_name": ai_name,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "attributes": attributes
        }

        # Update or append the entry in resources.jsonl
        resource_index_file = os.path.join(resource_dir, "resources.jsonl")
        updated = False
        new_content = []
        # make sure the resource_index_file exists
        if not os.path.exists(resource_index_file):
            open(resource_index_file, 'a').close()

        async with aiofiles.open(resource_index_file, "r+") as index:
            async for line in index:
                existing_entry = json.loads(line)
                if existing_entry['filename'] == file.filename and existing_entry['username'] == username:
                    existing_entry.update(resource_entry)  # Update existing entry
                    updated = True
                    new_content.append(json.dumps(existing_entry) + "\n")
                else:
                    new_content.append(line)

            if not updated:
                new_content.append(json.dumps(resource_entry) + "\n")  # Append new entry if not found

            # Rewind to start and write updated/new content
            await index.seek(0)
            await index.writelines(new_content)
            await index.truncate()  # Truncate to remove any leftover content
  
        return resource_entry


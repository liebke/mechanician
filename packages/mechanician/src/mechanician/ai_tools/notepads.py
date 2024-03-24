from mechanician.tools import AITools
from abc import ABC, abstractmethod
import json
import logging
import pprint
from datetime import datetime
import os

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


###############################################################################
## AI INSTRUCTIONS
###############################################################################

ai_instructions = f"""
      # Memory Management

      You are an AI assistant with access to tools for performing different tasks. 

      You also have been provided a `notepad`, so you can recall `notes` about the user you are interacting with. 

      You have a set of functions for managing these `notes`. 

      When the user provides you with information, you SHOULD store that information in your `notepad` as a `note` for later use.

      If you know the user's name, you should use it when addressing the user.

      When asked to perform a task, that may or may not require you to use an external tool, if there is information you need to complete that task that you do not currently know, then use your `notepad` functions to recall that information.

      If you do not find that information in your `notepad`, query the user and the store the relevant information from their response in your `notepad`,

      Be sure to include all relevant attributes of the `note` you are storing.

      Review the following `notes`, looking for user PREFERENCES, and use those PREFERENCES to guide your actions and interactions with the user.

      The following are the `notes` you have related to the current user:
      ----
      """

###############################################################################
## TOOL INSTRUCTIONS
###############################################################################
  
ai_tool_instructions = [
    {
      "type": "function",
      "function": {
        "name": "create_note",
        "description": "Creates a note with a name and a value, the value is either a string or a JSON serializable object with attributes representing the attributes of the note.",
        "parameters": {
          "type": "object",
          "properties": {
            "value": {
              "type": "object",
              "description": "This mandatory field must contain a string representing the body of the note or a complete and valid JSON object with all the required details of the note to be created, as specified by the user."
            },
            "name": {
              "type": "string",
              "description": "The name of the note to create. It must be a unique identifier within the note collection and using the same name as a previous note will update the value of that note."
            }
          },
          "required": [
            "value",
            "name"
          ]
        }
      }
    },

  {
    "type": "function",
    "function": {
      "name": "list_notes",
      "description": "List all notes in the current notepad.",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  },

  {
    "type": "function",
    "function": {
      "name": "get_note",
      "description": "Returns the note with a given name.",
      "parameters": {
        "type": "object",
        "properties": {
          "note_name": {
            "type": "string",
            "description": "The name of the note to return."
          }
        },
        "required": [
          "note_name"
        ]
      }
    }
  },

  {
    "type": "function",
    "function": {
      "name": "delete_note",
      "description": "Erases a note with a given name.",
      "parameters": {
        "type": "object",
        "properties": {
          "note_name": {
            "type": "string",
            "description": "The name of the note to delete."
          }
        },
        "required": [
          "note_name"
        ]
      }
    }
  },

  {
    "type": "function",
    "function": {
      "name": "get_current_datetime",
      "description": "Returns the current date and time as a string.",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  },

  {
    "type": "function",
    "function": {
      "name": "delete_notepad",
      "description": "Deletes all the contents of the current notepad.",
      "parameters": {
        "type": "object",
        "properties": {},
        "required": []
      }
    }
  },
]

###############################################################################
## NotepadStore Abstract Class
###############################################################################
  
class NotepadStore(ABC):
    @abstractmethod
    def create_note(self, name: str, value: str) -> str:
        pass

    @abstractmethod
    def list_notes(self) -> str:
        pass
    
    @abstractmethod
    def get_note(self, note_name: str) -> str:
        pass

    @abstractmethod
    def delete_note(self, note_name: str) -> str:
        pass
    
    @abstractmethod
    def delete_notepad(self) -> str:
        pass
    

###############################################################################
## NotepadFileStore
###############################################################################
    
class NotepadFileStore(NotepadStore):
    
    def __init__(self,
                 notepad_name: str,
                 notepad_directory_name: str = "notepads",):
        self.notepad_name = notepad_name
        self.notepad_directory_name = os.path.join(os.getcwd(), notepad_directory_name)
        self.notepad_file_path = os.path.join(self.notepad_directory_name, f"{self.notepad_name}.json")
        self.notepad = {}
        # if notepad directory does not exist, create it
        if not os.path.exists(self.notepad_directory_name):
            os.makedirs(self.notepad_directory_name)
        self.load_notepad()


    def load_notepad(self):
        if os.path.exists(self.notepad_file_path):
            with open(self.notepad_file_path, "r") as f:
                self.notepad = json.load(f)
        else:
            self.notepad = {}


    def save_notepad(self):
        with open(self.notepad_file_path, "w") as f:
            json.dump(self.notepad, f)


    def create_note(self, name: str, value: str) -> str:
        self.notepad[name] = value
        self.save_notepad()
        return f"Note {name} created with value {value}"


    def list_notes(self) -> str:
        return pprint.pformat(self.notepad)
    

    def get_note(self, note_name: str) -> str:
        if note_name in self.notepad:
            return self.notepad.get(note_name, None)
        else:
            return f"Note {note_name} not found"
        

    def delete_note(self, note_name: str) -> str:
        if note_name in self.notepad:
            del self.notepad[note_name]
            self.save_notepad()
            return f"Note {note_name} deleted"
        else:
            return f"Note {note_name} not found"
        

    def delete_notepad(self) -> str:
        os.remove(self.notepad_file_path)
        self.notepad = {}
        return f"Notepad {self.notepad_name} deleted"
    

###############################################################################
## NotepadAITools
###############################################################################
  
class NotepadAITools(AITools):

    def __init__(self,
                 notepad_store: NotepadStore,):
        self.notepad_name = notepad_store.notepad_name
        self.notepad_store = notepad_store

    ###############################################################################
    ## AI INSTRUCTIONS
    ###############################################################################

    def get_ai_instructions(self):
      return f"""{ai_instructions}\n{self.list_notes({})}"""
    

    def get_tool_instructions(self):
      return ai_tool_instructions
    

    def create_note(self, params:dict):
        name = params.get("name")
        if not name:
            resp = "Note name is required"
            logger.info(resp)
            return resp
        
        value = params.get("value")
        if not value:
            resp = "Note value is required"
            logger.info(resp)
            return resp
        
        resp = self.notepad_store.create_note(name, value)
        logger.info(resp)
        return resp
    

    def list_notes(self, params:dict):
        resp = self.notepad_store.list_notes()
        logger.info(resp)
        return resp
    

    def delete_note(self, params:dict):
        note_name = params.get("note_name")
        if not note_name:
            resp = "Note name is required"
            logger.info(resp)
            return resp
        
        resp = self.notepad_store.delete_note(note_name)
        logger.info(resp)
        return resp
    

    def delete_notepad(self, params:dict):
        resp = self.notepad_store.delete_notepad()
        logger.info(resp)
        return resp
    

    def get_current_datetime(self, params: dict):
        current_datetime = datetime.now().isoformat()
        resp = {"current_datetime": current_datetime}
        return resp

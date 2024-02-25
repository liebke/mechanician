from mechanician.tools.notepads import NotepadStore
from arango import ArangoClient
import json
import logging
import pprint
import os
import traceback
from mechanician_arangodb.document_manager import DocumentManager


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

class ArangoNotepadStore(NotepadStore):

    def __init__(self,
                 notepad_name: str,
                 arango_client: ArangoClient, 
                 database_name: str,
                 notepad_collection_name="notepads",
                 db_username: str = 'root' , 
                 db_password: str = None):
        self.notepad_name = notepad_name
        self.notepad_collection_name = notepad_collection_name
        if not arango_client:
            raise ValueError("Arango client is required.")
        if not database_name:
            raise ValueError("Database name is required.")
        logger.info(f"Initializing ArangoNotepadStore with database_name: {database_name}")
        db_username = db_username or os.getenv("ARANGO_USERNAME", None)
        db_password = db_password or os.getenv("ARANGO_PASSWORD", None)
        if (not db_username) or (not db_password):
            raise ValueError("ARANGO_USERNAME and ARANGO_PASSWORD are required.")
        self.doc_mgr = DocumentManager(arango_client, db_username, db_password)
        self.database_name = database_name
        self.database = self.doc_mgr.create_database(database_name)
        # Create a collection for notepads
        collection = self.doc_mgr.create_document_collection(self.database, self.notepad_collection_name)
        logger.debug(f"Notepad collection '{self.notepad_collection_name}' created.")

        # Get the current notepad
        if self.doc_mgr.document_exists(self.database, self.notepad_collection_name, self.notepad_name):
            self.notepad = self.doc_mgr.get_document(self.database, self.notepad_collection_name, self.notepad_name)
        else:
            self.notepad = self.doc_mgr.create_document(self.database, 
                                                        collection_name=self.notepad_collection_name, 
                                                        document_id=self.notepad_name, 
                                                        document={})
        # DEBUG
        logger.debug(f"Notepad '{self.notepad_name}' notes")
        logger.debug(pprint.pformat(self.notepad))
        # END DEBUG
            

  
    ###############################################################################
    ## NotePadStore
    ###############################################################################
   
    def create_note(self, name: str, value: str) -> str:
        try:
            if (name is None):
                resp = "name is required."
                logger.info(resp)
                return resp
            
            if (value is None):
                resp = "value is required."
                logger.info(resp)
                return resp
            
            self.notepad[name] = value
            doc = self.doc_mgr.add_field_to_document(self.database, self.notepad_collection_name, self.notepad_name, name, value)
            resp = f"Note '{name}' added to Notepad '{self.notepad_name}':"
            # DEBUG
            logger.debug(resp)
            # END DEBUG
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            traceback.print_exc()
            return f"ERROR: {message}"
        

    def list_notes(self) -> str:
        try:
            doc = self.doc_mgr.get_document(self.database, self.notepad_collection_name, self.notepad_name)
            resp =  json.dumps(doc, indent=2)
            # DEBUG
            logger.debug(f"Notes from Notepad '{self.notepad_name}':")
            logger.debug(pprint.pformat(resp))
            # END DEBUG
            return resp
        
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def get_note(self, note_name: str) -> str:
        try:
            if (note_name is None):
                resp = "note_name is required."
                # DEBUG
                logger.debug(resp)
                # END DEBUG
                return resp
                        
            note = self.notepad.get(note_name, None)
            resp = f"Note '{note_name}' from Notepad '{self.notepad_name}':\n"
            resp += pprint.pformat(note)
            # DEBUG
            logger.debug(resp)
            # END DEBUG
            return resp
        
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"


    def delete_note(self, note_name: str) -> str:
        try:
            if note_name is None:
                resp = "note_name is required."
                # DEBUG
                logger.debug("DELETE_NOTE RESP:")
                logger.debug(resp)
                # END DEBUG
                return resp

            deleted_note = self.notepad.pop(note_name, None)
            # Save updated notepad in ArangoDB
            resp = self.doc_mgr.delete_field_from_document(self.database, 
                                                           self.notepad_collection_name, 
                                                           self.notepad_name, 
                                                           note_name)
            # DEBUG
            logger.debug("DELETED_NOTE RESP:")
            logger.debug(resp)
            # END DEBUG
            if deleted_note is not None:
                resp = f"Note '{deleted_note}' deleted."
            else:
                resp = f"Note '{note_name}' does not exist."

            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            traceback.print_exc()
            return f"ERROR: {message}"
    

    def delete_notepad(self) -> str:
        # Delete the notepad
        try:
            self.doc_mgr.delete_document(self.database, self.notepad_collection_name, self.notepad_name)
            resp = f"Notepad '{self.notepad_name}' deleted."
            return resp
        
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
            

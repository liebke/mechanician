from mechanician.ai_tools import AITools
from arango import ArangoClient
import json
from mechanician_arangodb.document_manager import DocumentManager
import logging
import pprint

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


class DocumentManagerAITools(AITools):

    def __init__(self, 
                 client: ArangoClient, 
                 database_name: str,
                 username: str = 'root' , 
                 password: str = None):
        
        logger.info(f"Initializing DocumentManagerToolHandler with database_name: {database_name}")
        self.doc_mgr = DocumentManager(client, username, password)
        self.database_name = database_name
        self.database = self.doc_mgr.create_database(database_name)


    def create_document_collection(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            if not collection_name:
                resp = "collection_name is required."
                logger.info(resp)
                return resp
            
            collection = self.doc_mgr.create_document_collection(self.database, collection_name)
            resp = f"Collection '{collection_name}' created."
            # DEBUG
            logger.info(pprint.pformat(resp))
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def create_link_collection(self, input: dict):
        try:
            link_collection_name = input.get('link_collection_name')
            if not link_collection_name:
                resp = "link_collection_name is required."
                logger.info(resp)
                return resp
            
            link_collection = self.doc_mgr.create_link_collection(self.database, link_collection_name)
            resp = f"Link collection '{link_collection_name}' created."
            # DEBUG
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def delete_collection(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            if not collection_name:
                resp = "collection_name is required."
                logger.info(resp)
                return resp
            
            self.doc_mgr.delete_collection(self.database, collection_name)
            resp = f"Collection '{collection_name}' deleted."
            # DEBUG
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def create_document(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            document_id = input.get('document_id')
            document = input.get('document')
            if not collection_name or not document_id or not document:
                resp = "collection_name, document_id, and document are required."
                logger.info(resp)
                return resp
            
            doc = self.doc_mgr.create_document(self.database, collection_name, document_id, document)
            resp = f"Document '{document_id}' created in collection '{collection_name}': {json.dumps(doc, indent=2)}."
            # DEBUG
            logger.debug(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def add_field_to_document(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            document_id = input.get('document_id')
            field_name = input.get('field_name')
            field_value = input.get('field_value')
            if not collection_name or not document_id or not field_name or not field_value:
                resp = "collection_name, document_id, field_name, and field_value are required."
                logger.info(resp)
                return resp
            
            doc = self.doc_mgr.add_field_to_document(self.database, collection_name, document_id, field_name, field_value)
            resp = f"Document '{document_id}' updated in collection '{collection_name}' with field {field_name} = {field_value}."
            # DEBUG
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"

    def delete_document(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            document_id = input.get('document_id')
            if not collection_name or not document_id:
                resp = "collection_name and document_id are required."
                logger.info(resp)
                return resp
            
            doc = self.doc_mgr.delete_document(self.database, collection_name, document_id)
            resp = f"Document '{document_id}' has been deleted from collection '{collection_name}'."
            # DEBUG
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        
    
    def delete_link(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            link_id = input.get('link_id')
            if not collection_name or not link_id:
                resp = "collection_name and link_id are required."
                logger.info(resp)
                return resp
            
            doc = self.doc_mgr.delete_document(self.database, collection_name, link_id)
            resp = f"Link '{link_id}' has been deleted from collection '{collection_name}'."
            # DEBUG
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def get_document(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            document_id = input.get('document_id')
            if not collection_name or not document_id:
                resp = "collection_name and document_id are required."
                logger.info(resp)
                return resp
            doc = self.doc_mgr.get_document(self.database, collection_name, document_id)
            logger.debug(doc)
            return doc
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def link_documents(self, input: dict):
        try:
            source_collection_name = input.get('source_collection_name')
            source_document_id = input.get('source_document_id')
            target_collection_name = input.get('target_collection_name')
            target_document_id = input.get('target_document_id')
            link_collection_name = input.get('link_collection_name')
            if not source_collection_name or not source_document_id or not target_collection_name or not target_document_id or not link_collection_name:
                resp = "source_collection_name, source_document_id, target_collection_name, target_document_id, and link_collection_name are required."
                logger.info(resp)
                return resp
            link = self.doc_mgr.link_documents(self.database, source_collection_name, source_document_id, target_collection_name, target_document_id, link_collection_name)
            logger.info(f"Link created: {source_collection_name}/{source_document_id} -> {link_collection_name} -> {target_collection_name}/{target_document_id}")
            return
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def list_documents_linked_to(self, input: dict):
        try:
            target_collection_name = input.get('target_collection_name')
            target_document_id = input.get('target_document_id')
            from_collection_name = input.get('from_collection_name')
            link_collection_name = input.get('link_collection_name')
            if not target_collection_name or not target_document_id or not from_collection_name or not link_collection_name:
                resp = "target_collection_name, target_document_id, from_collection_name, and link_collection_name are required."
                logger.info(resp)
                return resp
            docs = self.doc_mgr.list_documents_linked_to(self.database, target_collection_name, target_document_id, from_collection_name, link_collection_name)
            return docs
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_documents_linked_from(self, input: dict):
        try:
            source_collection_name = input.get('source_collection_name')
            source_document_id = input.get('source_document_id')
            target_collection_name = input.get('target_collection_name')
            link_collection_name = input.get('link_collection_name')
            if not source_collection_name or not source_document_id or not target_collection_name or not link_collection_name:
                resp = "source_collection_name, source_document_id, target_collection_name, and link_collection_name are required."
                logger.info(resp)
                return resp
            docs = self.doc_mgr.list_documents_linked_from(self.database, source_collection_name, source_document_id, target_collection_name, link_collection_name)
            return docs
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_documents(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            if not collection_name:
                resp = "collection_name is required."
                logger.info(resp)
                return resp
            docs = self.doc_mgr.list_documents(self.database, collection_name)
            return docs
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_links(self, input: dict):
        try:
            collection_name = input.get('link_collection_name')
            if not collection_name:
                resp =  "link collection_name is required."
                logger.info(resp)
                return resp
            docs = self.doc_mgr.list_links(self.database, collection_name)
            return docs
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_inbound_links(self, input: dict):
        try:
            target_collection_name = input.get('target_collection_name')
            target_document_id = input.get('target_document_id')
            link_collection_name = input.get('link_collection_name')
            if not target_collection_name or not target_document_id or not link_collection_name:
                resp = "target_collection_name, target_document_id, and link_collection_name are required."
                logger.info(resp)
                return resp
            links = self.doc_mgr.list_inbound_links(self.database, target_collection_name, target_document_id, link_collection_name)
            return links
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"

    def list_inbound_links(self, input: dict):
        try:
            target_collection_name = input.get('target_collection_name')
            target_document_id = input.get('target_document_id')
            link_collection_name = input.get('link_collection_name')
            if not target_collection_name or not target_document_id or not link_collection_name:
                resp = "target_collection_name, target_document_id, and link_collection_name are required."
                logger.info(resp)
                return resp
            links = self.doc_mgr.list_inbound_links(self.database, target_collection_name, target_document_id, link_collection_name)
            return links
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_outbound_links(self, input: dict):
        try:
            source_collection_name = input.get('source_collection_name')
            source_document_id = input.get('source_document_id')
            link_collection_name = input.get('link_collection_name')
            if not source_collection_name or not source_document_id or not link_collection_name:
                resp = "source_collection_name, source_document_id, and link_collection_name are required."
                logger.info(resp)
                return resp
            links = self.doc_mgr.list_outbound_links(self.database, source_collection_name, source_document_id, link_collection_name)
            return links
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def list_document_collections(self, input: dict = None):
        try:
            collections = self.doc_mgr.list_document_collections(self.database)
            return collections
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_link_collections(self, input: dict = None):
        try:
            collections = self.doc_mgr.list_link_collections(self.database)
            return collections
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"


    def list_collections(self, input: dict = None):
        try:
            collections = self.doc_mgr.list_collections(self.database)
            return collections
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"

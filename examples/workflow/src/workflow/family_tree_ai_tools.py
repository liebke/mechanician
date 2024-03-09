from mechanician.ai_tools import AITools
from arango import ArangoClient
import json
from mechanician_arangodb.document_manager import DocumentManager
import logging
import pprint
import os

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


class FamilyTreeAITools(AITools):

    def __init__(self, 
                 client: ArangoClient, 
                 database_name: str,
                 username: str = 'root' , 
                 password: str = None):
        
        logger.info(f"Initializing FamilyTreeAITools with database_name: {database_name}")
        if not client:
            raise ValueError("Arango client is required.")
        if not database_name:
            raise ValueError("Database name is required.")
        username = username or os.getenv("ARANGO_USERNAME", None)
        password = password or os.getenv("ARANGO_PASSWORD", None)
        if (not username) or (not password):
            raise ValueError("ARANGO_USERNAME and ARANGO_PASSWORD are required.")
        self.doc_mgr = DocumentManager(client, username, password)
        self.database_name = database_name
        self.database = self.doc_mgr.create_database(database_name)
        self.collection_name = "individuals"
        self.create_collection({"collection_name": self.collection_name})
        self.link_collection_name = "relationships"
        self.create_link_collection({"link_collection_name": self.link_collection_name})


    def create_collection(self, input: dict):
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
    

    def add_individual(self, input: dict):
        try:
            print("ADD_INDIVIDUAL INPUT:")
            pprint.pprint(input)
            individual_id = input.get('id')
            individual_name = input.get('name')
            individual_born = input.get('born')
            individual_died = input.get('died')
            individual = {"name": individual_name, "born": individual_born, "died": individual_died, "id": individual_id}
            if not individual_name or not individual_id:
                resp = "name and id are required."
                logger.info(resp)
                return resp
            
            doc = self.doc_mgr.create_document(self.database, self.collection_name, individual_id, individual)
            resp = f"Individual '{individual_id}' created in collection '{self.collection_name}': {json.dumps(doc, indent=2)}."
            # DEBUG
            logger.debug(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def add_field_to_individual(self, input: dict):
        try:
            individual_id = input.get('id')
            field_name = input.get('field_name')
            field_value = input.get('field_value')
            if not self.collection_name or not individual_id or not field_name or not field_value:
                resp = "name, field_name, and field_value are required."
                logger.info(resp)
                return resp
            
            doc = self.doc_mgr.add_field_to_document(self.database, self.collection_name, individual_id, field_name, field_value)
            resp = f"Document '{individual_id}' updated in collection '{self.collection_name}' with field {field_name} = {field_value}."
            # DEBUG
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"


    def delete_individual(self, input: dict):
        try:
            individual_id = input.get('id')
            if not individual_id:
                resp = "id is required."
                logger.info(resp)
                return resp
            
            doc = self.doc_mgr.delete_document(self.database, self.collection_name, individual_id)
            resp = f"Document '{individual_id}' has been deleted from collection '{self.collection_name}'."
            # DEBUG
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        
    
    def delete_link(self, input: dict):
        try:
            link_id = input.get('link_id')
            if not link_id:
                resp = "link_id is required."
                logger.info(resp)
                return resp
            
            doc = self.doc_mgr.delete_document(self.database, self.collection_name, link_id)
            resp = f"Link '{link_id}' has been deleted from collection '{self.collection_name}'."
            # DEBUG
            logger.info(resp)
            return resp
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def get_individual(self, input: dict):
        try:
            individual_id = input.get('id')
            if not self.collection_name or not individual_id:
                resp = "individual_id is required."
                logger.info(resp)
                return resp
            doc = self.doc_mgr.get_document(self.database, self.collection_name, individual_id)
            logger.debug(doc)
            return doc
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def add_relationship(self, input: dict):
        try:
            print("ADD_RELATIONSHIP INPUT:")
            pprint.pprint(input)
            source_collection_name = self.collection_name
            from_individual = input.get('from')
            target_collection_name = self.collection_name
            to_individual = input.get('to')
            relationship_type = input.get('relationship_type')
            if not from_individual or not to_individual or not relationship_type:
                resp = "from, to, relationship_type are required."
                logger.info(resp)
                return resp
            link = self.doc_mgr.link_documents(self.database, source_collection_name, from_individual, target_collection_name, to_individual, self.link_collection_name)
            logger.info(f"Link created: {source_collection_name}/{from_individual} -> {self.link_collection_name} -> {target_collection_name}/{to_individual}")
            return
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
        

    def list_individuals_linked_to(self, input: dict):
        try:
            target_collection_name = self.collection_name
            to_individual = input.get('to')
            from_collection_name = self.collection_name
            if not to_individual:
                resp = "to is required."
                logger.info(resp)
                return resp
            docs = self.doc_mgr.list_documents_linked_to(self.database, target_collection_name, to_individual, from_collection_name, self.link_collection_name)
            return docs
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_individuals_linked_from(self, input: dict):
        try:
            source_collection_name = self.collection_name
            from_individual = input.get('from')
            target_collection_name = self.collection_name
            if not from_individual:
                resp = "from is required."
                logger.info(resp)
                return resp
            docs = self.doc_mgr.list_documents_linked_from(self.database, source_collection_name, from_individual, target_collection_name, self.link_collection_name)
            return docs
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_individuals(self, input: dict):
        try:
            docs = self.doc_mgr.list_documents(self.database, self.collection_name)
            return docs
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_relationships(self, input: dict):
        try:
            docs = self.doc_mgr.list_links(self.database, self.link_collection_name)
            return docs
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_inbound_links(self, input: dict):
        try:
            target_collection_name = self.collection_name
            to_individual = input.get('to')
            if not to_individual:
                resp = "to is required."
                logger.info(resp)
                return resp
            links = self.doc_mgr.list_inbound_links(self.database, target_collection_name, to_individual, self.link_collection_name)
            return links
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"

    def list_inbound_links(self, input: dict):
        try:
            target_collection_name = self.collection_name
            to_individual = input.get('to')
            if not to_individual:
                resp = "to is required."
                logger.info(resp)
                return resp
            links = self.doc_mgr.list_inbound_links(self.database, target_collection_name, to_individual, self.link_collection_name)
            return links
        except Exception as e:
            message = str(e)
            logger.error(f"ERROR: {message}")
            return f"ERROR: {message}"
    

    def list_outbound_links(self, input: dict):
        try:
            source_collection_name = self.collection_name
            from_individual = input.get('from')
            if not from_individual:
                resp = "from is required."
                logger.info(resp)
                return resp
            links = self.doc_mgr.list_outbound_links(self.database, source_collection_name, from_individual, self.link_collection_name)
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

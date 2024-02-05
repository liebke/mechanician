from mechanician.tool_handlers import ToolHandler
from arango import ArangoClient
import json
from mechanician_arangodb.document_manager import DocumentManager

class DocumentManagerToolHandler(ToolHandler):
    def __init__(self, 
                 client: ArangoClient, 
                 database_name: str,
                 username: str = 'root' , 
                 password: str = None):
        self.doc_mgr = DocumentManager(client, username, password)
        self.database_name = database_name
        self.database = self.doc_mgr.create_database(database_name)
        
    # def create_database(self, input: dict):
    #     db_name = input['db_name']
    #     db = self.doc_mgr.create_database(db_name)
    #     resp = f"Database '{db_name}' created."
    #     return resp
    
    # def delete_database(self, input: dict):
    #     db_name = input['db_name']
    #     self.doc_mgr.delete_database(db_name)
    #     resp = f"Database '{db_name}' deleted."
    #     return resp
    
    def create_document_collection(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            if not collection_name:
                return "collection_name is required."
            
            collection = self.doc_mgr.create_document_collection(self.database, collection_name)
            resp = f"Collection '{collection_name}' created."
            # DEBUG
            print(resp)
            return resp
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def create_link_collection(self, input: dict):
        try:
            link_collection_name = input.get('link_collection_name')
            if not link_collection_name:
                return "link_collection_name is required."
            
            link_collection = self.doc_mgr.create_link_collection(self.database, link_collection_name)
            resp = f"Link collection '{link_collection_name}' created."
            # DEBUG
            print(resp)
            return resp
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def delete_collection(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            if not collection_name:
                return "collection_name is required."
            
            self.doc_mgr.delete_collection(self.database, collection_name)
            resp = f"Collection '{collection_name}' deleted."
            # DEBUG
            print(resp)
            return resp
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def create_document(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            document_id = input.get('document_id')
            document = input.get('document')
            if not collection_name or not document_id or not document:
                return "collection_name, document_id, and document are required."
            
            doc = self.doc_mgr.create_document(self.database, collection_name, document_id, document)
            resp = f"Document '{document_id}' created in collection '{collection_name}': {json.dumps(doc, indent=2)}."
            # DEBUG
            print(resp)
            return resp
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def get_document(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            document_id = input.get('document_id')
            if not collection_name or not document_id:
                return "collection_name and document_id are required."
            doc = self.doc_mgr.get_document(self.database, collection_name, document_id)
            return json.dumps(doc, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def link_documents(self, input: dict):
        try:
            source_collection_name = input.get('source_collection_name')
            source_document_id = input.get('source_document_id')
            target_collection_name = input.get('target_collection_name')
            target_document_id = input.get('target_document_id')
            link_collection_name = input.get('link_collection_name')
            if not source_collection_name or not source_document_id or not target_collection_name or not target_document_id or not link_collection_name:
                return "source_collection_name, source_document_id, target_collection_name, target_document_id, and link_collection_name are required."
            link = self.doc_mgr.link_documents(self.database, source_collection_name, source_document_id, target_collection_name, target_document_id, link_collection_name)
            # DEBUG
            print(link)
            return json.dumps(link, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
        

    def list_documents_linked_to(self, input: dict):
        try:
            target_collection_name = input.get('target_collection_name')
            target_document_id = input.get('target_document_id')
            from_collection_name = input.get('from_collection_name')
            link_collection_name = input.get('link_collection_name')
            if not target_collection_name or not target_document_id or not from_collection_name or not link_collection_name:
                return "target_collection_name, target_document_id, from_collection_name, and link_collection_name are required."
            docs = self.doc_mgr.list_documents_linked_to(self.database, target_collection_name, target_document_id, from_collection_name, link_collection_name)
            return json.dumps(docs, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def list_documents_linked_from(self, input: dict):
        try:
            source_collection_name = input.get('source_collection_name')
            source_document_id = input.get('source_document_id')
            target_collection_name = input.get('target_collection_name')
            link_collection_name = input.get('link_collection_name')
            if not source_collection_name or not source_document_id or not target_collection_name or not link_collection_name:
                return "source_collection_name, source_document_id, target_collection_name, and link_collection_name are required."
            docs = self.doc_mgr.list_documents_linked_from(self.database, source_collection_name, source_document_id, target_collection_name, link_collection_name)
            return json.dumps(docs, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def list_documents(self, input: dict):
        try:
            collection_name = input.get('collection_name')
            if not collection_name:
                return "collection_name is required."
            docs = self.doc_mgr.list_documents(self.database, collection_name)
            return json.dumps(docs, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def list_links(self, input: dict):
        try:
            collection_name = input.get('link_collection_name')
            if not collection_name:
                return "link collection_name is required."
            docs = self.doc_mgr.list_links(self.database, collection_name)
            return json.dumps(docs, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def list_inbound_links(self, input: dict):
        try:
            target_collection_name = input.get('target_collection_name')
            target_document_id = input.get('target_document_id')
            link_collection_name = input.get('link_collection_name')
            if not target_collection_name or not target_document_id or not link_collection_name:
                return "target_collection_name, target_document_id, and link_collection_name are required."
            links = self.doc_mgr.list_inbound_links(self.database, target_collection_name, target_document_id, link_collection_name)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"

    def list_inbound_links(self, input: dict):
        try:
            target_collection_name = input.get('target_collection_name')
            target_document_id = input.get('target_document_id')
            link_collection_name = input.get('link_collection_name')
            if not target_collection_name or not target_document_id or not link_collection_name:
                return "target_collection_name, target_document_id, and link_collection_name are required."
            links = self.doc_mgr.list_inbound_links(self.database, target_collection_name, target_document_id, link_collection_name)
            return json.dumps(links, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def list_outbound_links(self, input: dict):
        try:
            source_collection_name = input.get('source_collection_name')
            source_document_id = input.get('source_document_id')
            link_collection_name = input.get('link_collection_name')
            if not source_collection_name or not source_document_id or not link_collection_name:
                return "source_collection_name, source_document_id, and link_collection_name are required."
            links = self.doc_mgr.list_outbound_links(self.database, source_collection_name, source_document_id, link_collection_name)
            return json.dumps(links, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
        

    def list_document_collections(self, input: dict):
        try:
            collections = self.doc_mgr.list_document_collections(self.database)
            return json.dumps(collections, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"
    

    def list_link_collections(self, input: dict):
        try:
            collections = self.doc_mgr.list_link_collections(self.database)
            return json.dumps(collections, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"


    def list_collections(self, input: dict):
        try:
            collections = self.doc_mgr.list_collections(self.database)
            return json.dumps(collections, indent=2)
        except Exception as e:
            message = str(e)
            return f"ERROR: {message}"

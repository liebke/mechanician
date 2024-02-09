from arango import ArangoClient
import os
import logging

logger = logging.getLogger(__name__)

class DocumentManager:

    def __init__(self, client: ArangoClient, username: str = 'root', password: str = None):
        self.client = client
        self.sys_db_name = '_system'
        self.username = username
        if password is None:
            self.password = os.getenv("ARANGO_ROOT_PASSWORD")
        else:
            self.password = password
        self.sys_db = self.client.db(self.sys_db_name, username=self.username, password=self.password)
        

    def create_database(self, db_name: str):

        if not self.sys_db.has_database(db_name):
            logger.info(f"Creating database '{db_name}'...")
            if self.sys_db.create_database(db_name) is True:
                logger.info(f"Database '{db_name}' created.")
                return self.client.db(db_name, username=self.username, password=self.password)
            
        else:
            logger.info(f"Database '{db_name}' already exists.")
            return self.client.db(db_name, username=self.username, password=self.password)


    def delete_database(self, db_name: str):
        if self.sys_db.has_database(db_name):
            self.sys_db.delete_database(db_name)
            logger.info(f"Database '{db_name}' deleted.")
        else:
            logger.info(f"Database '{db_name}' does not exist.")


    def create_document_collection(self, database, collection_name):
        if not database.has_collection(collection_name):
            collection = database.create_collection(collection_name)
            logger.info(f"Collection '{collection_name}' created.")
        else:
            collection = database.collection(collection_name)
            logger.info(f"Collection '{collection_name}' already exists.")
        return collection
    

    def delete_document(self, database, collection_name, document_id):
        collection = database.collection(collection_name)
        if collection.has(document_id):
            collection.delete(document_id)
            logger.info(f"Document '{document_id}' deleted.")


    def delete_link(self, database, collection_name, link_id):
        collection = database.collection(collection_name)
        if collection.has(link_id):
            collection.delete(link_id)
            logger.info(f"Link '{link_id}' deleted.")


    def create_link_collection(self, database, link_collection_name):
        if not database.has_collection(link_collection_name):
            link_collection = database.create_collection(link_collection_name, edge=True)
            logger.info(f"Link collection '{link_collection_name}' created.")
        else:
            link_collection = database.collection(link_collection_name)
            logger.info(f"Link collection '{link_collection_name}' already exists.")
        return link_collection


    def delete_collection(self, database, collection_name):
        if database.has_collection(collection_name):
            database.delete_collection(collection_name)
            logger.info(f"Collection '{collection_name}' deleted.")
        else:
            logger.info(f"Collection '{collection_name}' does not exist.")


    def create_document(self, database, collection_name, document_id: str, document: dict):
        document['_key'] = str(document_id)  # Create _key from integer ID
        collection = database.collection(collection_name)
        if collection.has(document['_key']):
            return collection.update(document)
        else:
            return collection.insert(document)
        
        
    def link_exists(self,
                    link_collection, 
                    from_collection_name: str,
                    from_document_id: str,
                    to_collection_name: str,
                    to_document_id: str):
        
        cursor = link_collection.find({'_from': f"{from_collection_name}/{from_document_id}", 
                                       '_to': f"{to_collection_name}/{to_document_id}"}, 
                                       limit=1)
        return cursor.count() > 0
        

    def link_documents(self,
                       database,
                       source_collection_name: str,
                       source_document_id: str,
                       target_collection_name: str,
                       target_document_id: str,
                       link_collection_name,
                       link_attributes: dict = None):
       
        link = {'_from': f"{source_collection_name}/{source_document_id}", 
                '_to': f"{target_collection_name}/{target_document_id}"}
        if link_attributes is not None:
            link = {**link, **link_attributes} # Merge the two dictionaries

        link_collection = database.collection(link_collection_name)
        if not self.link_exists(link_collection, 
                                source_collection_name, 
                                source_document_id,
                                target_collection_name,
                                target_document_id):
            link = link_collection.insert(link)
            logger.info(f"Link created from {source_document_id} to {target_document_id}.")
        else:
            logger.info(f"Link from {source_document_id} to {target_document_id} already exists.")
        

    def get_document(self, database, collection_name, obj_id: int):
        collection = database.collection(collection_name)
        return collection.get(str(obj_id))


    def list_documents_linked_to(self, 
                                 database, 
                                 target_collection_name: str,
                                 target_document_id: int, 
                                 from_collection_name: str,
                                 link_collection_name: str):
        query = f"""
                    FOR v IN 1..1 INBOUND '{target_collection_name}/{target_document_id}' {link_collection_name}
                    FILTER IS_SAME_COLLECTION('{from_collection_name}', v)
                    RETURN v
                    """
        # query = f"""
        #     FOR v IN 1..1 INBOUND '{parent_collection_name}/{start_vertex_id}' {link_collection_name}
        #     FILTER IS_SAME_COLLECTION('{child_collection_name}', v)
        #     RETURN {{'_id': v._id, 'name': v.name}}
        # """
        
        # Execute the AQL query
        cursor = database.aql.execute(query)
        # Return the result as a list
        return list(cursor)


    def list_documents_linked_from(self,
                                   database,
                                   source_collection_name: str, 
                                   source_document_id: int,
                                   target_collection_name: str,
                                   link_collection_name: str):
        query = f"""
        FOR v IN 1..1 OUTBOUND '{source_collection_name}/{source_document_id}' {link_collection_name}
            FILTER IS_SAME_COLLECTION('{target_collection_name}', v)
            RETURN v
        """
        cursor = database.aql.execute(query)
        return list(cursor)


    def list_documents(self, database, collection_name):
        collection = database.collection(collection_name)
        cursor = collection.all()
        return list(cursor)
    

    def list_links(self, database, link_collection_name):
        collection = database.collection(link_collection_name)
        cursor = collection.all()
        return list(cursor)


    def list_inbound_links(self, 
                           database, 
                           target_collection_name, 
                           target_document_id,
                           link_collection_name,):
        query = f"""
        FOR edge IN INBOUND '{target_collection_name}/{target_document_id}' {link_collection_name}
            RETURN edge
        """
        cursor = database.aql.execute(query)
        return list(cursor)


    def list_outbound_links(self, 
                            database, 
                            source_collection_name, 
                            source_document_id,
                            link_collection_name):
        query = f"""
        FOR edge IN OUTBOUND '{source_collection_name}/{source_document_id}' {link_collection_name}
            RETURN edge
        """
        logger.info(query)
        cursor = database.aql.execute(query)
        return list(cursor)


    def list_collections(self, database):
        return [col.get('name') for col in database.collections()
                if not col['name'].startswith('_')]
    

    def list_document_collections(self, database):
        collections = database.collections()
        non_edge_collection_names = [col.get('name') 
                                     for col in collections 
                                     if not database.collection(col.get('name')).properties().get('edge')
                                        and not col['name'].startswith('_')]
        return non_edge_collection_names
    

    def list_link_collections(self, database):
        collections = database.collections()
        edge_collection_names = [col.get('name') for col in collections 
                                 if database.collection(col.get('name')).properties().get('edge')
                                    and not col['name'].startswith('_')]
        return edge_collection_names
    
    def add_field_to_document(self, database, collection_name, document_id, field_name, field_value):
        collection = database.collection(collection_name)
        document = collection.get(document_id)
        document[field_name] = field_value
        return collection.update(document)

# For testing
from dotenv import load_dotenv
import random
from pprint import pprint
from arango import ArangoClient
from mechanician_arangodb.document_manager import DocumentManager
import logging

logger = logging.getLogger(__name__)


###############################################################################
## MAIN
###############################################################################

def main():
    load_dotenv()
    # Initialize the ArangoDB client
    client = ArangoClient(hosts='http://localhost:8529')
    doc_mgr = DocumentManager(client)

    # Create a new database for testing
    test_db_name = 'test_db'
    doc_mgr.create_database(test_db_name)
    # test_db = client.db(test_db_name, username='root', password=os.getenv("ARANGO_ROOT_PASSWORD"))
    test_db = doc_mgr.create_database(test_db_name)
    # Create test collections
    test_parent_collection_name = 'parent_objects'
    test_child_collection_name = 'child_objects'
    test_link_collection_name = 'child_of'
    test_parent_collection = doc_mgr.create_document_collection(test_db, test_parent_collection_name)
    test_child_collection = doc_mgr.create_document_collection(test_db, test_child_collection_name)
    test_child_of_link_collection = doc_mgr.create_link_collection(test_db, test_link_collection_name)

    # Insert test data
    parent_n = 10
    child_n = 20
    parent_objects = [{'id': i, 'name': f'parent_{i}'} for i in range(1, parent_n + 1)]
    child_objects = [{'id': i, 'name': f'child_{i}'} for i in range(1, child_n + 1)]

    # insert parent objects
    for parent in parent_objects:
        doc_mgr.create_document(test_db, test_parent_collection_name, str(parent['id']), parent)

    # insert child objects
    for child in child_objects:
        doc_mgr.create_document(test_db, test_child_collection_name, str(child['id']), child)

    # Create random links from parent objects to child objects
    for parent in parent_objects:
        for child in child_objects:
            if random.random() > 0.5:
                doc_mgr.link_documents(test_db,
                                       test_child_collection_name, 
                                       child['id'],
                                       test_parent_collection_name, 
                                       parent['id'], 
                                       test_link_collection_name,
                                       link_attributes={'relation': 'child_of'})
                
    # Get child object of a parent object
    parent = parent_objects[0]
    print(f"\n\nParent documents: {parent['name']}")
    pprint(doc_mgr.get_document(test_db, test_parent_collection_name, parent['id']))
    
    child_docs = doc_mgr.list_documents_linked_to(test_db, 
                                          test_parent_collection_name,
                                          parent['id'],
                                          test_child_collection_name,
                                          test_link_collection_name)

    # get child object
    child = child_objects[0]
    print(f"\n\nChild document: {child['name']}")

    print(f"\n\nChild document of {parent['name']}:")
    pprint(doc_mgr.get_document(test_db, test_child_collection_name, child['id']))

    parent_docs = doc_mgr.list_documents_linked_from(test_db, 
                                             test_child_collection_name,
                                             child['id'],
                                             test_parent_collection_name,
                                             test_link_collection_name)
    print(f"\n\nParent documents of {child['name']}:")
    # pprint(parent_docs)
    for parent in parent_docs:
        pprint({k : parent[k] for k in ['id', 'name'] if k in parent})



    child_docs = doc_mgr.list_documents_linked_to(test_db, 
                                          test_parent_collection_name,
                                          parent['id'],
                                          test_child_collection_name,
                                          test_link_collection_name,)
    print(f"\n\nChild documents of {parent['name']}:")
    # pprint(child_docs)
    for child in child_docs:
        pprint({k : child[k] for k in ['id', 'name'] if k in child})


    # print(f"\n\nList incoming of links of {parent['name']}:")
    # # pprint(doc_mgr.list_documents(test_db, test_link_collection_name))
    # pprint(doc_mgr.list_incoming_links(test_db, test_link_collection_name, test_parent_collection_name, parent['id']))

    # print(f"\n\nList outgoing of links of {parent['name']}:")
    # pprint(doc_mgr.list_outgoing_links(test_db, test_link_collection_name, test_child_collection_name, child['id']))    


    print(f"\n\nList all collections:")
    pprint(doc_mgr.list_collections(test_db))

    print(f"\n\nList all link collections:")
    pprint(doc_mgr.list_link_collections(test_db))

    ###########################################################################
    # Delete test collections
    doc_mgr.delete_collection(test_db, test_parent_collection_name)
    doc_mgr.delete_collection(test_db, test_child_collection_name)
    doc_mgr.delete_collection(test_db, test_link_collection_name)

    # Delete test database
    doc_mgr.delete_database(test_db_name)



if __name__ == '__main__':
    main()



import chromadb
from chromadb.utils import embedding_functions
from mechanician.resources import ResourceConnector, ResourceConnectorProvisioner
from mechanician_chroma.util import get_collection_name

###############################################################################
## ChromaUserAIConnectorProvisioner
###############################################################################
    
class UserAIChromaConnectorProvisioner(ResourceConnectorProvisioner):    

        def create_connector(self, context: dict={}):
            # Use the context to control access to resources provided by the connector.
            # ...
            username = context.get("username")
            ai_name = context.get("ai_name")
            collection_name = get_collection_name(username, ai_name)
            return ChromaConnector(collection_name=collection_name)


###############################################################################
## ChromaConnectorProvisioner
###############################################################################
    
class ChromaConnectorProvisioner(ResourceConnectorProvisioner):
        
        def __init__(self, collection_name):
            self.collection_name = collection_name
    

        def create_connector(self, context: dict={}):
            # Use the context to control access to resources provided by the connector.
            # ...
            return ChromaConnector(collection_name=self.collection_name)


###############################################################################
## ChromaConnector
###############################################################################

# docker run -p 8080:8000 chromadb/chroma
class ChromaConnector(ResourceConnector):
    def __init__(self, collection_name, data_path="./data/chromadb"):
        self.collection_name = collection_name
        self.data_path = data_path
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        

    def get_collection(self):
        chroma_client = chromadb.HttpClient(host='127.0.0.1', port=8080)
        return chroma_client.get_or_create_collection(name=self.collection_name,
                                                      embedding_function=self.embedding_func,
                                                      metadata={"hnsw:space": "cosine"})


    def chroma_query(self, params):
        prompt = params.get("prompt")
        results = self.get_collection().query(query_texts=[prompt],
                                              n_results=20)
        documents = results.get("documents")[0]
        metadatas = results.get("metadatas")[0]
        data = []
        for i in range(len(documents)):
            data.append({"source": metadatas[i].get("source"), "text": documents[i]})

        return [{"name": "prompt", "data": prompt},
                {"name": "context", "data": data}]
    

    def preprocess_prompt(self, prompt):
        return self.chroma_query({"prompt": prompt})
    

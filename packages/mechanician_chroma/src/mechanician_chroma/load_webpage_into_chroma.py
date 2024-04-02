# pip install requests
# pip install beautifulsoup4
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import CharacterTextSplitter
from chromadb.utils import embedding_functions
import chromadb
import argparse

CHUNK_SIZE = 500
CHUNK_OVERLAP = 20

def load_url_into_chroma(collection_name, url):
    # Fetch webpage content
    response = requests.get(url)
    webpage_content = response.text
    # Use BeautifulSoup to parse the HTML content and extract text
    soup = BeautifulSoup(webpage_content, "html.parser")
    text_content = soup.get_text()

    text_splitter = CharacterTextSplitter(
        separator = "\n",
        chunk_size = CHUNK_SIZE,
        chunk_overlap = CHUNK_OVERLAP,
    )
    splits = text_splitter.split_text(text_content)
    metadata = []
    split_id = 0
    for split in splits:
        metadata.append({"source": url, "split": split_id})
        split_id += 1

    # get url name
    url_name = url.split("/")[-1]
    ids = []
    i = 0
    for split in splits:
        ids.append(f"{url_name}_{i}")
        i += 1

    # Initialize ChromaDB
    # chroma_client = chromadb.PersistentClient(path="./data/chromadb")
    chroma_client = chromadb.HttpClient(host='127.0.0.1', port=8080)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = chroma_client.get_or_create_collection(name=collection_name,
                                                 embedding_function=embedding_func,
                                                 metadata={"hnsw:space": "cosine"})
    print(f"collections: {chroma_client.list_collections()}")
    if collection_name not in [collection.name for collection in chroma_client.list_collections()]:
        print(f"Creating collection: {collection_name}")
        collection = chroma_client.create_collection(name=collection_name)
    else:
        print(f"Fetching collection: {collection_name}")
        collection = chroma_client.get_collection(name=collection_name)
    document_id = url
    collection.add(
        documents=splits,  # Add the webpage text content as a document
        metadatas=metadata,  # Metadata about the document source
        ids=ids
    )
    return collection



def main(collection_name, url):
    # Your code here
    print(f"URL: {url}")
    print(f"Collection name: {collection_name}")
    load_url_into_chroma(collection_name, url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that loads a webpage into a Chroma Vector Database.")
    parser.add_argument("-u", "--url", help="The URL", required=True)
    parser.add_argument("-c", "--collection", help="The name of the collection", required=True)
    args = parser.parse_args()

    main(args.collection, args.url)

# Example usage:    
# scripts/load_webpage.sh -c "studio_demo_collection" -u "https://en.wikipedia.org/wiki/Mechanician"
# scripts/load_webpage.sh -c "studio_demo_collection" -u "https://en.wikipedia.org/wiki/Artificial_intelligence"
# scripts/load_webpage.sh -c "studio_demo_collection" -u "https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)"

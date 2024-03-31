from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
import chromadb
# pip install PyPDF2
import PyPDF2
import argparse


CHUNK_SIZE = 500
CHUNK_OVERLAP = 20

def load_pdf_into_chroma(collection_name, pdf_path):
    # Now we can load our PDF in PyPDF2 from memory
    # pip install PyPDF2
    # get pdf name
    pdf_name = pdf_path.split("/")[-1]
    read_pdf = PyPDF2.PdfReader(pdf_path)
    count = len(read_pdf.pages)
    pages_txt = []
    # For each page we extract the text
    for i in range(count):
        page = read_pdf.pages[i]
        pages_txt.append({"page_id": i, "text": page.extract_text()})

    # We return the PDF name as well as the text inside each pages
    # return pdf_name, pages_txt
    load_text_into_chroma(collection_name, pdf_name, pdf_path, pages_txt)
    
    


def load_text_into_chroma(collection_name, doc_id, doc_source, doc_pages:list[dict]):
    # Initialize ChromaDB
    # chroma_client = chromadb.PersistentClient(path="./data/chromadb")
    chroma_client = chromadb.HttpClient(host='127.0.0.1', port=8080)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = chroma_client.get_or_create_collection(name=collection_name,
                                                        embedding_function=embedding_func,
                                                        metadata={"hnsw:space": "cosine"})

    if collection_name not in [collection.name for collection in chroma_client.list_collections()]:
        collection = chroma_client.create_collection(name=collection_name)
    else:
        collection = chroma_client.get_collection(name=collection_name)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    for page in doc_pages:
        splits = text_splitter.split_text(page.get("text"))
        metadata = []
        split_id = 0
        for split in splits:
            page_id = page.get("page_id")
            source = f"{doc_source}/{page_id}"
            metadata.append({"source": source, "split": split_id})
            split_id += 1

        # get url name
        ids = []
        i = 0
        for split in splits:
            ids.append(f"{doc_id}_{page_id}_{i}")
            i += 1

        collection.add(
            documents=splits,  # Add the webpage text content as a document
            metadatas=metadata,  # Metadata about the document source
            ids=ids)


def main(file_path, collection_name):
    # Your code here
    print(f"File path: {file_path}")
    print(f"Collection name: {collection_name}")
    load_pdf_into_chroma(collection_name, file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that loads a PDF document into a Chroma Vector Database.")
    parser.add_argument("-f", "--file", help="The path to the file", required=True)
    parser.add_argument("-c", "--collection", help="The name of the collection", required=True)
    args = parser.parse_args()

    main(args.file, args.collection)

# Example usage:
# scripts/load_pdf.sh -f /Users/davidliebke/Documents/learning_llms/papers/attention_is_all_you_need.pdf -c wikipedia_collection
# scripts/load_pdf.sh --collection wikipedia_collection --file ~/Documents/learning_llms/papers/bedrock-ug.pdf
# scripts/load_pdf.sh --collection wikipedia_collection --file ~/Documents/learning_llms/papers/mixtral_7b.pdf

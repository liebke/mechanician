from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from chromadb.utils import embedding_functions
import chromadb
import argparse
from pprint import pprint

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 10

def load_excel_into_chroma(collection_name, excel_path):
    csv_name = excel_path.split("/")[-1]
    loader = UnstructuredExcelLoader(excel_path, mode="elements")
    docs = loader.load()
    print(f"doc count: {len(docs)}")
    print(f"doc: {docs[10].page_content}")
    print(f"metadata: {docs[10].metadata}")
    print("HTML: ")
    print(docs[10].metadata.get('text_as_html'))

    # read_pdf = PyPDF2.PdfReader(excel_path)
    # count = len(read_pdf.pages)
    # pages_txt = []
    # # For each page we extract the text
    # for i in range(count):
    #     page = read_pdf.pages[i]
    #     pages_txt.append({"page_id": i, "text": page.extract_text()})

    # # We return the PDF name as well as the text inside each pages
    # # return pdf_name, pages_txt
    # load_text_into_chroma(collection_name, csv_name, excel_path, docs)
    
    


def load_text_into_chroma(collection_name, doc_id, doc_source, docs:list[dict]):
    # Initialize ChromaDB
    # chroma_client = chromadb.PersistentClient(path="./data/chromadb")
    chroma_client = chromadb.HttpClient(host='127.0.0.1', port=8080)
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = chroma_client.get_or_create_collection(name=collection_name,
                                                        embedding_function=embedding_func,
                                                        metadata={"hnsw:space": "cosine"})


    # if collection_name not in [collection.name for collection in chroma_client.list_collections()]:
    #     collection = chroma_client.create_collection(name=collection_name)
    # else:
    #     collection = chroma_client.get_collection(name=collection_name)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )
    for doc in docs:
        splits = text_splitter.split_text(doc.page_content)
        print(f"split count: {len(splits)}")
        print(f"split: {splits[0]}")
        metadata = []
        split_id = 0
        for split in splits:
            page_id = doc.metadata.get("page_id")
            source = f"{doc_source}/{page_id}"
            metadata.append({"source": source, "split": split_id})
            split_id += 1

        ids = []
        i = 0
        for split in splits:
            ids.append(f"{doc_id}_{page_id}_{i}")
            i += 1
        print("IDS: ")
        pprint(ids)
        # collection.add(
        #     documents=splits,  # Add the webpage text content as a document
        #     metadatas=metadata,  # Metadata about the document source
        #     ids=ids)


def main(file_path, collection_name):
    # Your code here
    print(f"File path: {file_path}")
    print(f"Collection name: {collection_name}")
    load_excel_into_chroma(collection_name, file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A script that loads a Excel spreadsheets into a Chroma Vector Database.")
    parser.add_argument("-f", "--file", help="The path to the file", required=True)
    parser.add_argument("-c", "--collection", help="The name of the collection", required=True)
    args = parser.parse_args()

    main(args.file, args.collection)

# Example usage:
# scripts/load_excel.sh -f /Users/davidliebke/Documents/learning_llms/papers/spreadsheet.xlsx -c studio_demo_collection

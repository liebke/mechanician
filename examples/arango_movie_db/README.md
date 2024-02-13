# Daring Mechanician Arango Movie Database

## Getting Started with the Arango Movie Database Example

This example project uses the ArangoDB graph database and the mechanician-arangodb package to provide a **Movie Database Assistant** that records information on movies, their casts, and reviews.

* [examples/arango_movie_db](https://github.com/liebke/mechanician/tree/main/examples/arango_movie_db)

## The Arango Document Manager AI Tools

This project uses the generic **DocumentManagerAITools** class from the mechanician-arangodb package to interact with the ArangoDB graph database.

* **create_document_collection**: Creates a document collection in the database
* **create_link_collection**: Creates an link collection in the database
* **delete_collection**: Deletes a collection from the database
* **delete_document**: Deletes a document from a collection
* **delete_link**: Deletes a link from a collection
* **create_document**: Creates a document in a collection
* **add_field_to_document**: Adds a field to a document in a collection
* **link_documents**: Links two documents in a collection
* **get_document**: Retrieves a document from a collection
* **list_documents_linked_to**: Lists all documents in the target collection that are linked from the source document.
* **list_documents_linked_from**: Lists all documents in the target collection that are linked to the source document.
* **list_documents**: Lists all documents in a collection
* **list_links**: Lists all links in a collection
* **list_inbound_links**: Lists all inbound links to a document.
* **list_outbound_links**: Lists all outbound links from a document.
* **list_document_collections**: Lists all document collections in the database
* **list_link_collections**: Lists all link collections in the database
* **list_collections**: Lists all collections in the database



### Arango Movie Database Example Code

* [```examples/arango_movie_db/main.py```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/src/main.py): TODO. 

* [```mechanician_arangodb document_ai_tools.py```](https://github.com/liebke/mechanician/blob/main/packages/mechanician_arangodb/src/mechanician_arangodb/document_ai_tools.py): are the AITools available to the AI.

* [```examples/arango_movie_db/instructions/instructions.json```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/instructions/instructions.json): is a set of instructions for the AI that inform it of the tools available to it, and describe its role as a **Movie Database Assistant** that records information on movies, their casts, and reviews.

* [```example_prompts.md```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/example_prompts.md): provides a variety of approaches to interacting with the AI.

* [```examples/arango_movie_db/test_ai.py```](https://github.com/liebke/mechanician/blob/main/examples/arango_movie_db/src/test_ai.py): shows how to test **Daring Mechanician** programs by having an AI-driven set of tasks. 



## Install

Create a virtual environment and install the requirements.

```bash
conda create -n arango_movie_db_env python=3.11
conda activate arango_movie_db_env
```

Install the example project using pip:

```bash
pip install -e .
```

Set up your environment variables or create a `.env` file with the following variables:

```bash
ARANGO_ROOT_PASSWORD=<YOUR_ARANGO_DATABASE_PASSWORD>
ARANGO_HOST=http://localhost:8529
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>

```


#### Run ArangoDB in Docker

```bash
docker pull arangodb/arangodb
```

```bash
docker run -e ARANGO_ROOT_PASSWORD=${ARANGO_ROOT_PASSWORD} -p 8529:8529 -d --name arangodb-instance arangodb/arangodb
```

```bash
docker stop arangodb-instance
```

```bash
docker start arangodb-instance
```

#### Run the interactive TAG AI shell:

```bash
./scripts/run.sh
```

### Run the AI-Driven tests:

```bash
./scripts/test.sh
```


## Exit the Virtual Environment and Clean Up

```bash
conda deactivate
conda remove --name arango_movie_db_env --all
```
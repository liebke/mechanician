# Daring Mechanician Arango Movie Database

## Getting Started with the Arango Movie Database Example

This example project uses the ArangoDB graph database and the mechanician-arangodb package to provide a **Movie Database Assistant** that records information on movies, their casts, and reviews.

* [examples/arango_movie_db](https://github.com/liebke/mechanician/tree/main/examples/arango_movie_db)

This project uses the generic **DocumentManagerAITools** class from the mechanician-arangodb package to interact with the ArangoDB graph database, the tools have not been customized but the instructions provided to the AI are focused on create documents related to movies and movie reviews.

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
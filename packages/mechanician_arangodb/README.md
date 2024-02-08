
## Run ArangoDB in Docker

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


### Create a Virtual Environment (optional)

Using [*Conda*](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-python) for environment management:

```bash
conda create --name mechanician_arangodb_env
conda activate mechanician_arangodb_env
```

* When it's time to remove the environment, use the following command:

```bash
conda deactivate
conda env remove --name mechanician_arangodb_env
```

### Install Dependencies

```bash
./install.sh
```

### Run Tests

Create .env file with the following content:

```bash


OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
MODEL_NAME=gpt-4-1106-preview
CALL_TOOLS_IN_PARALLEL=True
MAX_THREAD_WORKERS=10
ARANGO_ROOT_PASSWORD=<YOUR_ARANGODB_ROOT_PASSWORD>
ARANGO_HOST=http://localhost:8529

TMDB_API_KEY=<YOUR_TMDB_API_KEY>
TMDB_READ_ACCESS_TOKEN=<YOUR_TMDB_READ_ACCESS_TOKEN>
```


Install Mechanician OpenAI package and run tests:

```bash
cd ../mechanician_openai
./install.sh
cd ../mechanician_arangodb
./test.sh
```
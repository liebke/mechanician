
# Daring Mechanician-ArangoDB

This package provides **Daring Mechanician** `AITools` for interacting with ArangoDB graph databases.

See [Daring Mechanician Github Repo](https://github.com/liebke/mechanician) for more information.

```python
from mechanician_arangodb import DocumentManagerAITools
from arango import ArangoClient
```

```python
arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
doc_tools = DocumentManagerAITools(arango_client, database_name=database_name)
```

```python
ai = TAGAI(ai_connector=ai_connector, 
           instruction_set_directory="./instructions",
           tools=doc_tools,
           name="Movie Document Manager AI")
```


Example project:
* [examples/arango_movie_db](https://github.com/liebke/mechanician/tree/main/examples/arango_movie_db)


## Run ArangoDB in Docker

Set your environment variables:

```bash
ARANGO_ROOT_PASSWORD=<YOUR_ARANGODB_ROOT_PASSWORD>
ARANGO_HOST=http://localhost:8529
```

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


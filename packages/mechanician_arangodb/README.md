
# Daring Mechanician-ArangoDB

This package provides **Daring Mechanician** `AITools` for interacting with ArangoDB graph databases.

See [Daring Mechanician Github Repo](https://github.com/liebke/mechanician) for more information.


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

```bash
ARANGO_ROOT_PASSWORD=<YOUR_ARANGODB_ROOT_PASSWORD>
ARANGO_HOST=http://localhost:8529
```

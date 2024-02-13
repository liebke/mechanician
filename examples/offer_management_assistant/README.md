# Daring Mechanician Offer Management Example Application

## Install

Create a virtual environment and install the requirements.

```bash
conda create -n offer_mgmt_env python=3.11
conda activate offer_mgmt_env
```

Install the example project.

```bash
pip install -e .
```


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

## Run Interactive Example

```bash
./run.sh
```

## Run Tests
    
```bash
./test.sh
```

## Exit the Virtual Environment and Clean Up

```bash
conda deactivate
conda remove --name offer_mgmt_env --all
```
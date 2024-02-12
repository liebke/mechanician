# Daring Mechanician Arango Movie Database

## Install

Create a virtual environment and install the requirements.

```bash
conda create -n arango_movie_db_env python=3.11
conda activate arango_movie_db_env
```

Install the requirements from PyPI.

```bash
pip install mechanician_openai
pip install mechanician_arangodb
pip install -e .
```

or install all the requirements from a cloned Mechanician repository.

```bash
./install.sh
```

## Run Interactive Example

```bash
./scripts/run.sh
```

## Run Tests
    
```bash
./scripts/test.sh
```

## Exit the Virtual Environment and Clean Up

```bash
conda deactivate
conda remove --name arango_movie_db_env --all
```
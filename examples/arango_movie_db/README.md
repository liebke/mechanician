# Daring Mechanician Arango Movie Database

## Install

Create a virtual environment and install the requirements.

```bash
conda create -n arango_movie_db_env python=3.11
conda activate arango_movie_db_env
```

Install the example project.

```bash
pip install -e .
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
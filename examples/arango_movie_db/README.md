# Daring Mechanician Arango Movie Database

## Install

Create a virtual environment and install the requirements.

```bash
conda create -n arango_movie_db_env python=3.11
conda activate arango_movie_db_env
```

Install the requirements.

```bash
./install.sh
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
conda remove --name arango_movie_db_env --all
```
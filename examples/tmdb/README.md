# Daring Mechanician TMDb Example Application

# Daring Mechanician Arango Movie Database

## Install

Create a virtual environment and install the requirements.

```bash
conda create -n tmdb_env python=3.11
conda activate tmdb_env
```

Install the requirements from PyPI.

```bash
pip install mechanician_openai
pip install -e .
```

or install all the requirements from a cloned Mechanician repository.

```bash
./install.sh
```

### Set Environment Variables

You will need an [**OPENAI_API_KEY**](https://platform.openai.com/api-keys) and a [**TMDB_READ_ACCESS_TOKEN**](https://developers.themoviedb.org/3/getting-started/introduction) to run the example.


```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>
export TMDB_READ_ACCESS_TOKEN=<YOUR_TMDB_READ_ACCESS_TOKEN_HERE>
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
conda remove --name tmdb_env --all
```
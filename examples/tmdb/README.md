# Daring Mechanician TMDb Example Application

The TMDb example uses the The Movie Database (TMDb) API to provide a **Movie Database Assistant** that answers questions about movies and their casts and crews.

### The TMDb AI Tools

* **get_movie_credits**: Returns a list of cast and crew members for a movie given its ID that can be retrieved from the search_movie function
* **get_actor_credits**: Returns a list of movies that a person been in given their ID that can be retrieved from the search_person function
* **get_movie_by_id**: Returns a movie given its ID that can be retrieved from the search_movie function
* **search_movie**: Returns a list of movies given a search query
* **get_person_by_id**: Returns a person given their ID that can be retrieved from the search_person function
* **display_movie_poster**: Displays the poster for a movie given its ID that can be retrieved from the search_movie function


### Example Interaction

You can see from following interaction example, that it takes the AI four steps and four different tools to answer the question. 

```markdown
> what was the first movie that the actor that plays Furiosa in the upcoming movie Furiosa star in?

Applying tool: search_movie...
Applying tool: get_movie_by_id...
Applying tool: get_movie_credits...
Applying tool: get_actor_credits...


The first movie that Anya Taylor-Joy, the actor who plays Furiosa in the upcoming movie "Furiosa: A Mad Max Saga," starred in was "The Witch," where she played the character Thomasin. The film was released in 2015.

> 
```

* First it searches for the movie "Furiosa",
* then gets the movie's credits,
* then it gets the credits for the actor that plays Furiosa in the movie,
* and finally, it gets the credits for the first movie that actor starred in.


### TMDb Example Code

* [```examples/tmdb/main.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/main.py): shows how to use **Daring Mechanician** to interact with *OpenAI's Chat API*, providing it with **tools** that can be used by the LLM to makes *callouts* to other programs. 

* [```tmdb_tool_schemas.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/tmdb_tool_schemas.py): informs the LLM what tools are available to it.

* [```tmdb_tools.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/tmdb_tools.py): is *function_handler* containing ```stub``` functions that are invoked when the LLM makes one or more ```tool_call``` requests.

* [```examples/tmdb/instructions.md```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/instructions.md): is a set of instructions for the LLM that inform it of the tools available to it, and describe its role as a **Movie Database Assistant** that answers questions about movies and their casts and crews.

* [```tmdb_example_prompts.md```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/tmdb_example_prompts.md): provides a variety of approaches to interacting with the LLM.

* [```examples/tmdb/test.py```](https://github.com/liebke/mechanician/blob/main/examples/tmdb/test.py): shows how to test **Daring Mechanician** programs by having the AI self-evaluate their responses given a testing rubric. 


## Install

Create a virtual environment and install the requirements.

```bash
conda create -n tmdb_env python=3.11
conda activate tmdb_env
```

Install the example project.

```bash
pip install -e .
```

### Set Environment Variables

You will need an [**OPENAI_API_KEY**](https://platform.openai.com/api-keys) and a [**TMDB_READ_ACCESS_TOKEN**](https://developers.themoviedb.org/3/getting-started/introduction) to run the example.

Set up your environment variables or create a `.env` file with the following variables:

```bash
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>
TMDB_READ_ACCESS_TOKEN=<YOUR_TMDB_READ_ACCESS_TOKEN_HERE>
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
conda remove --name tmdb_env --all
```
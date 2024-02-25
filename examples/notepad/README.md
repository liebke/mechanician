<img src="../../docs/images/dm_notepads_1600x840.png" alt="Daring Mechanician Notepads"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">


## Notepads Provide LLMs Context Across Multiple Sessions

The focus of the [Daring Mechanician](https://mechanician.ai/daring-mechanician) project is on building tools for AIs to use, and *notepads* are one of the oldest tools around.

### Notepads Vs ChatGPT Memory

*Daring Mechanician* ***Notepads*** are inspired by the recent announcement of [ChatGPT memory](https://openai.com/blog/memory-and-new-controls-for-chatgpt) by *OpenAI*, meant to provide context about each user across multiple ChatGPT sessions.

*Notepads* provide the same functionality as ChatGPT's memory but a way that provides additional flexibility in what is remembered in different contexts.

### Different Notepads for Different Contexts

A *Notepad* can be specific to a user, a project, an activity, a location, or any other context that is useful to remember across multiple sessions.

### Notepads Tools

Telling the AI a fact will, usually, cause it to write a *note* in its *Notepad*, and you can ask it to remember a fact explicitly.

You can ask the AI to list all the *notes* in its *Notepad*, to delete a *note*, or to delete the entire *Notepad*.

The *Notepads* tools also include a method to get the current date and time, which can be useful for adding a timestamp to a *note*.

### Notepad Storage

Notepads can be stored in a local file or in an ArangoDB database, using the `NotepadFileStore` and `ArangoNotepadStore` classes, respectively.

#### NotepadFileStore

```python
from mechanician.tools.notepad import NotepadFileStore
```

```python
notepad_file_store = NotepadFileStore(notepad_name=notepad_name,
                                      notepad_directory_name=notepad_directory_name)
```

#### ArangoNotepadStore

```python
from mechanician_arangodb.notepad_store import ArangoNotepadStore
from mechanician_arangodb import ArangoClient
```

```python
database_name="test_notepad_db"
notepad_collection_name="notepads"
arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
arango_notepad_store = ArangoNotepadStore(notepad_name=notepad_name,
                                          arango_client=arango_client, 
                                          database_name=database_name,
                                          notepad_collection_name=notepad_collection_name,
                                          db_username=os.getenv("ARANGO_USERNAME"),
                                          db_password=os.getenv("ARANGO_PASSWORD"))
```

```python
arango_notepad_tools = NotepadAITools(notepad_store=arango_notepad_store)
```

### NotepadAITools

The `NotepadAITools` class provides the methods for AIs to interact with *Notepads*, including the following methods:

* create_note
* list_notes
* delete_note
* delete_notepad
* get_current_datetime



```python
from mechanician.tools.notepad import NotepadAITools
```

```python
notepad_tools = NotepadAITools(notepad_store=notepad_file_store)
```

#### Self-Explanatory AITools

The `NotepadAITools` class can be described as "self-explanatory", meaning it provides `get_tool_instructions` and `get_ai_instructions` methods that the `TAGAI` can use to get instructions on their use.

This means that you don't need to pass the `TAGAI` the `ai_instructions` and `tool_instructions` parameters, as it can get them from the `NotepadAITools` instance.

```python
from mechanician import TAGAI, shell

ai = TAGAI(ai_connector=ai_connector, 
           tools=notepad_tools,
           name="Notepad-Enabled AI")

shell.run(ai)
```


### Combining Notepads with Other AITools

*Notepads* can be combined with other *AITools* to enable the AI pass facts from the *Notepad* as parameters to other tools without needing to prompt the user for information it already knows from its *Notepad*.

For example, in the Notepad Example project, the AI can use the `get_weather` method of the `MiddleEarthWeatherAITools` class to get the weather at a location it knows from its *Notepad* and use the `current_datetime` tool get the time to pass.

#### Passing Multiple AITools to a TAGAI

You can pass multiple *AITools* to a *TAGAI* by passing a list of *AITools* to the `tools` parameter.

```python
from mechanician.tools.weather import MiddleEarthWeatherAITools
```

```python
weather_tools = MiddleEarthWeatherAITools()
```

```python
ai = TAGAI(ai_connector=ai_connector, 
           tools=[notepad_tools, weather_tools],
           name="Notepad-Enabled AI")
```

Each instance of `AITools` should use the same "self-explanatory" approach as `NotepadAITools`.

The default `get_ai_instructions` and `get_tool_instructions` methods of the `AITools` class with look for the existence of either `self.ai_instructions` or `self.tool_instructions` and return those if they exist.

Otherwise they will look for the exitence of `self.instruction_set_directory`, `self.tool_instruction_file_name`, and `self.ai_instruction_file_name` and use those to read the instructions for their respective files. 
 
But if none of those exist, they will use the default values of `./instructions` for the `instruction_set_directory` and `tool_instructions.json` and `ai_instructions.md` for the `tool_instruction_file_name` and `ai_instruction_file_name`, respectively, 
 
Finally, if the `instruction_set_directory` doesn't exist, `get_ai_instructions` will return an empty string and `get_tool_instructions` will return an empty list.



## The Notepads Example Project

See the [Notepad Example (NEED TO UPDATE TO MAIN BRANCH)](https://github.com/liebke/mechanician/tree/workflow/examples/notepad) for more details on how to use the *Notepads* tools.


### Install

Create a virtual environment and install the requirements.

```bash
conda create -n notepad_ex_env python=3.11
conda activate notepad_ex_env
```

Install the example project using pip:

```bash
pip install -e .
```

### Run the AI Shell

```bash
./scripts/run.sh --notepad "my_notepad"
```


## Exit the Virtual Environment and Clean Up

Exit the virtual environment and remove it when you are done.

```bash
conda deactivate
conda remove --name notepad_ex_env --all
```








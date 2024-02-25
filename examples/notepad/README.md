<img src="../../docs/images/dm_notepads_1600x840.png" alt="Daring Mechanician Notepads"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">


# Daring Mechanician Notepads Example

## Getting Started with the Notepads Example


## Install

Create a virtual environment and install the requirements.

```bash
conda create -n notepad_ex_env python=3.11
conda activate notepad_ex_env
```

Install the example project using pip:

```bash
pip install -e .
```


## Exit the Virtual Environment and Clean Up

```bash
conda deactivate
conda remove --name notepad_ex_env --all
```


## Code

Import the Notepad tools, TAGAI, and shell.

```python
from mechanician.tools.notepad import NotepadAITools, NotepadFileStore
from mechanician import TAGAI, shell
```

Read the notepad name from the command line arguments:

```python
import sys

for i in range(1, len(sys.argv)):
    if sys.argv[i] == "--notepad":
        notepad = sys.argv[i + 1]
```


Create a NotepadFileStore
 
```python
notepad_file_store = NotepadFileStore(notepad_name=notepad_name,
                                      notepad_directory_name=notepad_directory_name)
```

Create a NotepadAITools instance and add it to the AI.

```python
notepad_tools = NotepadAITools(notepad_store=notepad_file_store)
```

```python
ai = TAGAI(ai_connector=ai_connector, 
           tools=notepad_tools,
           name="Notepad-Enabled AI")
```

```python
shell.run(ai)
```

### Notepad Tools

* create_note
  * name
  * value
* list_notes
* delete_note
  * name
* delete_notepad
* get_current_datetime


## Provide Multiple AITools to a TAGAI

```python
ex_tools = ExampleAITools()
ai = TAGAI(ai_connector=ai_connector, 
           tools=[ex_tools, notepad_tools],
           name="Notepad-Enabled AI")
```


Implement the `get_ai_instructions` and `get_tool_instructions` methods, making your AITools Self-Explanatory.

```python
class ExampleAITools(AITools):

    def get_tool_instructions(self):
        ex_tool_instructions = []
        with open("./instructions/tool_instructions.json", "r") as f:
            ex_tool_instructions = json.load(f)
        return ex_tool_instructions
    

    def get_ai_instructions(self):
        ex_ai_instructions = ""
        with open("./instructions/ai_instructions.md", "r") as f:
            ex_ai_instructions = f.read()
        return ex_ai_instructions

    def get_weather(self, params):
        ...
```
<img src="docs/images/dm_architecture_1600x840.png" alt="Daring Mechanician"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">

>*"...if they could only have found the point of application for it, they would have constructed a lever capable of raising the earth and rectifying its axis. It was just this deficiency which baffled these **daring mechanicians**."*  -Jules Verne, *From the Earth to the Moon* (1865)


The [**Daring Mechanician** ](https://mechanician.ai) project provides several Python packages for building Generative AI-enabled applications where the AIs themselves are provided tools to use, an approach that can be described as **Tool Augmented Generation** (**TAG**), and the tool-wielding Generative AIs can be described as **Tool Augmented Generative AIs** (**TAG AIs**).

The core `mechanician` package provides modules for building, testing, and tuning *TAG AIs* and the tools that these AIs use, including support for AI-driven testing and AI-assisted *tuning* of the instruction sets given to an AI that we call **Instruction Auto-Tuning** (IAT). 

The `mechanician-studio` package provides a multi-user web interface for interacting with the tool-equipped AIs.

The `mechanician-openai` package provides `AIConnectors` for both OpenAI's *Chat* API and *Assistants* API, and there are plans to create connectors for more LLMs with *tool-call* support, especially local LLMs.

The `mechanician-arangodb` package provides an example of `AITools` that let AIs interact with the [ArangoDB](https://arangodb.com) graph database.

The `mechanician-chroma` package provides an example of a `ResourceConnector` for the [Chroma](https://docs.trychroma.com) Embeddings database that enables `PromptTools` to use Chroma as a resource for `PromptTemplates`.


# Mechanician Studio

The `mechanician-studio` package provides a multi-user web interface where each user has their own personal instances of PromptTools and AIs equipped with AITools that can all be customized to each user. For instance in the following screenshot the user interacts with an AI with access to a user-specific Notepad tool that lets it read and take notes, providing a mechanism for the AI to remember details about the user across multiple interactions.


<img src="docs/images/notepad_todo_animated.gif" alt="Daring Mechanician Studio Login"  style="max-width: 100%; height: auto float: right;">



## Prompt Tools: CRM Query

In the following screenshot, the user uses Prompt Tools that let them create *prompts* using Prompt Templates that are populated by queries to a CRM system. After entering the query parameters and clicking the "Generate Prompt" button, the user is presented with the query results, referred to as Prompt Resources, and a *generated prompt* that merges these resources into the Prompt Template at the top of the screen. Clicking on the "Send Prompt" button sends the generated prompt to the AI, which then generates a response.

<img src="docs/images/event_invite_animated.gif" alt="Daring Mechanician Studio Prompt Tools Event Invite"  style="max-width: 100%; height: auto float: right;">


## Prompt Tools: Vector Database Query

In the following screenshots, the user uses Prompt Tools that let them create *prompts* using Prompt Templates that are populated by queries to a Chroma vector database.

<img src="docs/images/chroma_query_animated_1.gif" alt="Daring Mechanician Studio Prompt Tools Chroma Query 1"  style="max-width: 100%; height: auto float: right;">

Once the prompt has been generated you can *send* it to the AI, which will generate a response based on the prompt.

<img src="docs/images/chroma_query_animated_2.gif" alt="Daring Mechanician Studio Prompt Tools Chroma Query 2"  style="max-width: 100%; height: auto float: right;">



## Mechanician Studio Example

The `mechanician-studio` package provides a multi-user web interface for interacting with the tool-equipped AIs.

See the [Mechanician Studio Example](https://github.com/liebke/mechanician/tree/main/examples/studio_demo) for a demonstration of how to use the `mechanician-studio` package.

The following Mechanician Studio examples shows a setup with 2 customized AIs, two different AITools, *Notepads* and *TMDb*, and two different PromptTools, *CRM* and *Chroma*.


## MechanicianStudio Class

```python
from mechanician_studio import MechanicianStudio

studio = MechanicianStudio(ai_provisioners=[ai_provisioner_notepad_only, ai_provisioner_tmdb],
                                            prompt_tools_provisioners=[crm_tools_provisioner, 
                                                                       chroma_tools_provisioner])
```

## AIConnectorProvisioner Class

```python
from mechanician_openai import OpenAIChatConnectorProvisioner

ai_connector_provisioner = OpenAIChatConnectorProvisioner(api_key=os.getenv("OPENAI_API_KEY"), 
                                                          model_name=os.getenv("OPENAI_MODEL_NAME"))
```

## AIProvisioner Class

```python
from mechanician import AIProvisioner

ai_provisioner_tmdb = AIProvisioner(ai_connector_provisioner=ai_connector_provisioner,
                                    name = "TMDB AI",
                                    ai_tools_provisioners = [notepad_tools_provisioner,
                                                             tmdb_tools_provisioner])
```

```python
ai_provisioner_notepad_only = AIProvisioner(ai_connector_provisioner=ai_connector_provisioner,
                                            name = "Notepad Only AI",
                                            ai_tools_provisioners = [notepad_tools_provisioner])
```

## AIToolsProvisioner Class

```python
from studio_demo.tmdb_ai_tools import TMDbAIToolsProvisioner

tmdb_tools_provisioner = TMDbAIToolsProvisioner(api_key=os.getenv("TMDB_READ_ACCESS_TOKEN"))
```

See [tmdb_ai_tools.py](https://github.com/liebke/mechanician/blob/main/examples/studio_demo/src/studio_demo/tmdb_ai_tools.py) for More Details


```python
from mechanician_arangodb.notepad_store import ArangoNotepadStoreProvisioner
from arango import ArangoClient

arango_client = ArangoClient(hosts=os.getenv("ARANGO_HOST"))
notepad_store_provisioner = ArangoNotepadStoreProvisioner(arango_client=arango_client, 
                                                          database_name="test_notepad_db",
                                                          notepad_collection_name="notepads",
                                                          db_username=os.getenv("ARANGO_USERNAME"),
                                                          db_password=os.getenv("ARANGO_PASSWORD"))
notepad_tools_provisioner = UserNotepadAIToolsProvisioner(notepad_store_provisioner=notepad_store_provisioner)
```

## PromptToolsProvisioner Class

```python
from mechanician.tools import PromptToolsProvisioner
from mechanician.chroma import ChromaConnectorProvisioner

chroma_connector_provisioner = ChromaConnectorProvisioner(collection_name="studio_demo_collection")

chroma_tools_provisioner = PromptToolsProvisioner(resource_connector_provisioner = chroma_connector_provisioner,
                                                  prompt_template_directory="./templates",
                                                  prompt_instructions_directory="./src/instructions",
                                                  prompt_tool_instruction_file_name="rag_prompt_tool_instructions.json") 
```
See [chroma_connector.py](https://github.com/liebke/mechanician/blob/main/packages/mechanician_chroma/src/mechanician_chroma/chroma_connector.py) for More Details

```python
from studio_demo.crm_connector import CRMConnectorProvisioner

crm_connector_provisioner = CRMConnectorProvisioner(crm_data_directory="./data")
crm_tools_provisioner = PromptToolsProvisioner(resource_connector_provisioner = crm_connector_provisioner,
                                               prompt_template_directory="./templates",
                                               prompt_instructions_directory="./src/instructions",
                                               prompt_tool_instruction_file_name="crm_prompt_tool_instructions.json") 
```

See [crm_connector.py](https://github.com/liebke/mechanician/blob/main/packages/mechanician_chroma/src/mechanician_chroma/crm_connector.py) for More Details


## Run Mechanician Studio

### SSL Certificates for Local Development: mkcert

https://github.com/FiloSottile/mkcert

```bash
brew install mkcert
mkcert -install
```

```bash
mkdir certs
mkcert -key-file ./certs/key.pem -cert-file ./certs/cert.pem localhost 127.0.0.1 ::1
```

```bash
export SSL_KEYFILE="./certs/key.pem"
export SSL_CERTFILE="./certs/cert.pem"
```

```bash
uvicorn.run("mechanician_studio.main:app", host="127.0.0.1", port=8000, ssl_keyfile="./certs/key.pem", ssl_certfile="./certs/cert.pem")
```

```python
import uvicorn

uvicorn.run(studio, 
            host="0.0.0.0", 
            port=8000,
            ssl_keyfile=os.getenv("SSL_KEYFILE"),
            ssl_certfile=os.getenv("SSL_CERTFILE"))
```

<img src="../../docs/images/dm_templates_1600x840.png" alt="Daring Mechanician Notepads"  style="max-width: 100%; height: auto float: right;">

<p style="clear: both; margin-top: 0; font-family: 'Tratatello', serif; color: darkgrey;">


# Daring Mechanician Prompt Templates & Tools

### Overview


When should you use prompt templates that are populated with dynamic calls to your back-end data to provide grounding data to the AI versus when should you have the AI use tool calls to get the data for itself?

You can populate a prompt template dynamically with data or you can have the AI use tool-calls to dynamically retrieve the data after it has been prompted, but when should you use one approach versus the other?

In cases where you know ahead of time about what a prompt should look like and you have created a prompt template, and you know exactly what data you need to provide the AI to provide a grounded answer, then it makes sense to use a prompt template populated with dynamic calls to your back-end data.

On the other hand, if you don't know ahead of time what the prompt is going to be, or you don't know what data the AI is going to need to provide a grounded answer, then it makes sense to have the AI use tool calls to get the data for itself.

In the case, where you don't just want the AI to retrieve data but also to perform some action, then you would use a tool call.

Prompt Templates, Actions (i.e. Tool Calls) can be used together to provide grounding data to the AI and to have the AI perform actions.

Prompt Templates provide a method of you applications to interact with the AI, and Tool Calls provide a method for the AI to interact with your applications.

In Copilot-like scenarios where the interactions are conversational, you would rely on tool-calls to provide the AI with the data it needs to provide a grounded anwswer.


## Prompt Templates

```markdown
You are {{event.organizer}}, and you are writing to your {{contact.relationship}} {{contact.name.first}} 
{{contact.name.last}} from the family {{contact.family[0]}} living at {{contact.address}}. Your purpose 
is to extend a heartfelt invitation to {{event.title}} at {{event.location}} on {{event.date}} - 
an event not to be missed, with merriment, tales, and a feast fit for the Shire's finest.

Instructions:
"""
Generate a subject line that captivates the curiosity and interest of {{contact.name}} using their 
known interest in {{contact.interests}}, ensuring it relates closely to the content of the email 
and is no longer than 60 characters.
Employ language that is warm, inviting, and direct, echoing the camaraderie and simple joys that 
define hobbit culture. Avoid any form of verbosity or convoluted expressions.
Gently encourage your {{contact.name}} to reply, expressing your eagerness to hear of their attendance 
and any inquiries they might have regarding the celebration.
Include details of the birthday feast: the date, time, location, and a hint at the special surprises 
you have in store for them.
Conclude with a hearty invitation to join in the festivities, making it clear how much their presence 
would add to the joy of the occasion.
"""

Now, generate the invitation to your hobbit friends.
```

### Prompt Resources

* ```{{event.organizer}}```
* ```{{contact.relationship}}``` 
* ```{{contact.name.first}}```
* ```{{contact.name.last}}```
* ```{{contact.family[0]}}```
* ```{{contact.address}}```
* ```{{event.title}}```
* ```{{event.location}}```
* ```{{event.date}}```
* ```{{contact.interests}}```



### Middle Earth CRM Data

[crm.json](https://github.com/liebke/mechanician/blob/main/examples/prompt_templates/crm_data.json)

```json
{
    "contacts": [
        {
            "name": {
                "first": "Lobelia",
                "last": "Sackville-Baggins"
            },
            "address": "Hardbottle, The Shire",
            "relationship": "Unwelcome relative",
            "interests": [
                "Snooping",
                "Acquiring silver spoons",
                "Intruding on Bag End"
            ],
            "family": [
                "Sackville-Baggins family"
            ]
        },
        ...
    ],
 
    "events": [
        {
            "title": "Bilbo's Eleventy-First Birthday",
            "date": "22 September 1401 Shire Reckoning",
            "location": "Bag End, Hobbiton, Westfarthing",
            "organizer": "Bilbo Baggins"
        },
        {
            "title": "Frodo's Farewell Party",
            "date": "22 September 1418 Shire Reckoning",
            "location": "Bag End, Hobbiton, Westfarthing",
            "organizer": "Frodo Baggins"
        }
    ]
}
```

### Command

```bash
> /call event_invite template=party_invite.md event="Eleventy-First Birthday" contact="Lobelia Sackville-Baggins"
```

### Generated Prompt

```markdown
You are Bilbo Baggins, and you are writing to your Unwelcome relative Lobelia Sackville-Baggins from the 
family Sackville-Baggins family living at Hardbottle, The Shire. Your purpose is to extend a heartfelt 
invitation to Bilbo's Eleventy-First Birthday at Bag End, Hobbiton, Westfarthing on 22 September 3001 - 
an event not to be missed, with merriment, tales, and a feast fit for the Shire's finest.

Instructions:
"""
Generate a subject line that captivates the curiosity and interest of 
{'first': 'Lobelia', 'last': 'Sackville-Baggins'} using their known interest in 
['Snooping', 'Acquiring silver spoons', 'Intruding on Bag End'], ensuring it relates closely to the 
content of the email and is no longer than 60 characters.
Employ language that is warm, inviting, and direct, echoing the camaraderie and simple joys that 
define hobbit culture. Avoid any form of verbosity or convoluted expressions.
Gently encourage your {'first': 'Lobelia', 'last': 'Sackville-Baggins'} to reply, expressing your 
eagerness to hear of their attendance and any inquiries they might have regarding the celebration.
Include details of the birthday feast: the date, time, location, and a hint at the special surprises 
you have in store for them.
Conclude with a hearty invitation to join in the festivities, making it clear how much their presence 
would add to the joy of the occasion.
"""

Now, generate the invitation to your hobbit friends.
```

### Invitation

```markdown
Subject: Discover Bag End's Secrets: A Grand Birthday Feast!

Dear Lobelia,

I hope this message finds you in good health and high spirits, surrounded by the many comforts of Hardbottle. 
As the leaves begin to shift from their summer green to the rich golds and ambers of early fall, an occasion 
of great importance and merriment is swiftly approaching—an occasion I believe would be greatly diminished 
without your distinctive presence.

It is with a joyful heart and open doors that I extend to you this heartfelt invitation to my Eleventy-First 
Birthday celebration, to be held at Bag End, Hobbiton, in the lush precincts of Westfarthing, on the 22nd of 
September, 3001, beginning as the sun dips below the horizon and continuing under the twinkling canopy of 
the night sky.

Anticipate a feast that promises to delight and surprise, where the ale flows as freely as the rivers of the 
Shire and the dishes tell tales of lands both near and far. And yes, Lobelia, there will indeed be a few 
specially reserved surprises—perhaps even a glimpse into the many curious treasures that have found their way 
into Bag End over the years, much to the delight of those with an eye for the unique and the extraordinary.

I understand, dear Lobelia, that your interests lie in the more unique aspects of hobbit gatherings, and I 
assure you, this birthday will offer moments of intrigue and discovery that would satisfy even the most 
ardent of curiosity-seekers. It would be a pleasure to share these moments with you, to hear your laughter 
mixing with the evening's festivities, and to perhaps exchange a story or two about our adventures and the 
simple yet profound joy they bring.

I eagerly await your reply, with hopes that you will grace us with your attendance. Should you have any 
questions or require details about the event, do not hesitate to get in touch. Your presence would 
undoubtedly add a significant layer of charm and vivacity to the evening’s celebrations.

Please consider this not just an invitation, but a sincere request for your company, as we come together 
to celebrate not just another year past, but the enduring spirit of friendship and family that unites us 
all, regardless of our differences.

With warmest regards and anticipation,

Bilbo Baggins
```

### Prompt Templates & Tools Example Project

[Example Project](https://github.com/liebke/mechanician/tree/main/examples/prompt_templates)

### Prompt Resources

```python
contact_resource = PromptResource("contact", contact)
event_resource = PromptResource("event", event)
```

### Prompt Templates

[party_invite.md](https://github.com/liebke/mechanician/blob/main/examples/prompt_templates/templates/party_invite.md)

```python
read_prompt_template(prompt_template_name,
                     template_directory="./templates")
```

### Generate Prompt

```python
generate_prompt(prompt_template, [contact_resource, event_resource])
```

### MiddleEarthCRMPromptTools

[crm_prompt_tools.py](https://github.com/liebke/mechanician/blob/64fbc65f8eba19183a831294d0015cf5c8178082/examples/prompt_templates/src/prompt_templates/main.py#L84)

```python
from mechanician.prompting.templates import PromptTemplate
from mechanician.prompting.tools import PromptTools

class MiddleEarthCRMPromptTools(PromptTools):
    def __init__(self, prompt_template_directory="./templates"):
        self.prompt_template_directory = prompt_template_directory
        self.crm = MiddleEarthCRM()


    def event_invite(self, params):
        prompt_template_name = params.get("template")
        event_title = params.get("event")
        contact_name = params.get("contact")

        contact = self.crm.lookup_contact_by_name(contact_name)        
        event = self.crm.lookup_event_by_title(event_title)

        prompt_template = PromptTemplate(template_filename=prompt_template_name, 
                                         template_directory=self.prompt_template_directory)

        prompt_template.add_resource("contact", contact)
        prompt_template.add_resource("event", event)
        
        return prompt_template.generate_prompt()
    

```

## Install

Create a virtual environment and install the requirements.

```bash
conda create -n dm_prompt_template_env python=3.11
conda activate dm_prompt_template_env
```

Install the example project using pip:

```bash
pip install -e .
```

#### Run the interactive TAG AI shell:

```bash
./scripts/run.sh
```


## Exit the Virtual Environment and Clean Up

```bash
conda deactivate
conda remove --name dm_prompt_template_env --all
```
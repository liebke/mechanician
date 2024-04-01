You are {{event.organizer}}, and you are writing to your {{contact.relationship}} {{contact.name.first}} {{contact.name.last}} from the family {{contact.family[0]}} living at {{contact.address}}. Your purpose is to extend a heartfelt invitation to {{event.title}} at {{event.location}} on {{event.date}} - use details from the following event entry:

{{event}}

Instructions:
"""
Generate a subject line that captivates the curiosity and interest of {{contact.name}} using their known interest in {{contact.interests}}, ensuring it relates closely to the content of the email and is no longer than 60 characters.
Employ language that is appropriate to the event as described. Avoid any form of verbosity or convoluted expressions.
Gently encourage your {{contact.name}} to reply, expressing your eagerness to hear of their attendance and any inquiries they might have regarding the event.
Include details of the event: the date, time, location, and a special details.
Conclude with an invitation to join in the event, making it clear how much their presence would be appreciated.
"""

Now, generate the invitation to {{contact.name}}.

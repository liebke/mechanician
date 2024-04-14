from typing import Dict, List
from pprint import pprint
import traceback
from mechanician.events import EventHandler
from mechanician_chroma.load_pdf_into_chroma import extract_text_from_pdf, load_pdf_into_chroma
from mechanician_chroma.util import get_collection_name

class PDFResourceUploadedEventHandler(EventHandler):

    def __init__(self, event_filters:Dict[str, List[str]]=None):
        # event_filters is a dictionary that maps event attributes to lists of values that the attribute must match
        self.event_filters = event_filters


    async def handle(self, context, event):
        try:
            if self.event_filters:
                for attr, values in self.event_filters.items():
                    if event.get(attr) not in values:
                        return
                    
            resource_entry = event.get("resource_entry")
            username = resource_entry.get("username")
            ai_name = resource_entry.get("ai_name")
            filename = resource_entry.get("filename")
            file_path = resource_entry.get("file_path")
            file_type = resource_entry.get("file_type")
            conversation_id = resource_entry.get("conversation_id")
            if not file_type.startswith("application/pdf"):
                return
            
            content = extract_text_from_pdf(file_path)
            prompt = f"""The user has uploaded a file called {filename} of type {file_type}. 
            Use the text below to answer questions from the user on the uploaded document.
            ----------------
            
            {content}

            ----------------
            """
            msg = {"role": "system", "content": prompt}

            print("PDF RESOURCE UPLOADED EVENT HANDLER:")
            pprint(event)
            print("\n\n\n")
            pprint(msg)

            ai_instance=context.get_ai_instance(username=username, 
                                                ai_name=ai_name,
                                                conversation_id=conversation_id)
            context.user_data_store.append_message_to_conversation(username, ai_name, conversation_id, msg)
            ai_instance.ai_connector.messages.append(msg)
            return
        except Exception as e:
            traceback.print_exc()



class ChromaPDFResourceUploadedEventHandler(EventHandler):

    def __init__(self, event_filters:Dict[str, List[str]]=None):
        # event_filters is a dictionary that maps event attributes to lists of values that the attribute must match
        self.event_filters = event_filters


    async def handle(self, context, event):
        try:
            if self.event_filters:
                for attr, values in self.event_filters.items():
                    if event.get(attr) not in values:
                        return
                    
            resource_entry = event.get("resource_entry")
            resource_id = resource_entry.get("resource_id")
            username = resource_entry.get("username")
            ai_name = resource_entry.get("ai_name")
            filename = resource_entry.get("filename")
            file_path = resource_entry.get("file_path")
            file_type = resource_entry.get("file_type")
            conversation_id = resource_entry.get("conversation_id")
            if not file_type.startswith("application/pdf"):
                return
            
            # content = extract_text_from_pdf(file_path)
            collection_name = get_collection_name(username, ai_name)
            load_pdf_into_chroma(collection_name, file_path)
            prompt = f"""The user has uploaded a file called {filename} of type {file_type}. 
            Use the `query` function to retrieve relevant sections of the document in order to
            answer questions from the user on the uploaded document.
            """
            msg = {"role": "system", "content": prompt}

            print("CHROMA PDF RESOURCE UPLOADED EVENT HANDLER:")
            pprint(event)
            print("\n\n\n")
            pprint(msg)

            ai_instance=context.get_ai_instance(username=username, 
                                                ai_name=ai_name,
                                                conversation_id=conversation_id)
            context.user_data_store.append_message_to_conversation(username, ai_name, conversation_id, msg)
            ai_instance.ai_connector.messages.append(msg)
            return
        except Exception as e:
            traceback.print_exc()



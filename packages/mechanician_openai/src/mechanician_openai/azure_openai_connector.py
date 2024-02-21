from openai import AzureOpenAI
from mechanician.util import SimpleStreamPrinter
import os
from mechanician_openai.chat_ai_connector import OpenAIChatConnector
import logging

logger = logging.getLogger(__name__)


class AzureOpenAIChatConnector(OpenAIChatConnector):
    
    DEFAULT_API_VERSION = "2023-12-01-preview"
    
    def __init__(self,
                 base_url=None,
                 azure_openai_key=None,
                 azure_openai_model_name=None,
                 azure_openai_api_version=None,
                 stream_printer = SimpleStreamPrinter(),
                 max_thread_workers=None):
        
        print(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
        print(f"AZURE_OPENAI_KEY: {os.getenv('AZURE_OPENAI_KEY')}")
        print(f"AZURE_OPENAI_MODEL_NAME: {os.getenv('AZURE_OPENAI_MODEL_NAME')}")
              
        base_url = base_url or os.getenv("AZURE_OPENAI_BASE_URL")
        api_key = azure_openai_key or os.getenv("AZURE_OPENAI_KEY")
        if api_key is None:
            raise ValueError("Azure OpenAI API Key is required")
    
        model_name = azure_openai_model_name or os.getenv("AZURE_OPENAI_MODEL_NAME")
        if model_name is None:
            raise ValueError("Azure OpenAI Model Name is required")
        
        azure_openai_api_version = azure_openai_api_version or os.getenv("AZURE_OPENAI_API_VERSION", self.DEFAULT_API_VERSION)
        
        client = AzureOpenAI(api_key=api_key,  
                             api_version=azure_openai_api_version,
                             base_url=base_url,
                            )
        
        super().__init__(client=client, 
                         model_name=model_name,
                         base_url=base_url,
                         api_key=api_key,
                         stream_printer=stream_printer, 
                         max_thread_workers=max_thread_workers)
   
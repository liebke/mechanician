from abc import ABC, abstractmethod
import os
import json
import logging
from typing import Any, List
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)

###############################################################################
## RESOURCE CONNECTOR
###############################################################################
        
class ResourceConnector(ABC):

    def query(self, query_name:str, params:dict=None):
        try:            
            if hasattr(self, query_name):
                meth = getattr(self, query_name)
                
                if meth:
                    if params is None:
                        response = meth()
                        if response is not None:
                            return {"status": "success", "resources": response}
                    else:
                        response = meth(params)
                        if response is not None:
                            return {"status": "success", "resources": response}
            else:
                error_msg = f"Unknown function: {query_name}"
                logger.info(error_msg)
                return {"status": "success", "resources": error_msg}
            
        except Exception as e:
            error_msg = f"Error calling function {query_name}: {e}"
            logger.error(error_msg)
            # Return empty response so that it's skipped
            return {"status": "error", "resources": error_msg}



###############################################################################
## RESOURCE CONNECTOR FACTORY
###############################################################################

class ResourceConnectorFactory(ABC):

    @abstractmethod
    def create_connector(self, context:dict={}):
        pass


###############################################################################
## RESOURCES
###############################################################################

class PromptResource:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data

    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]
        else:
            raise AttributeError(f"'PromptResource' object has no attribute '{attr}'")

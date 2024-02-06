from abc import ABC, abstractmethod
import json
import logging

logger = logging.getLogger('mechanician.tool_handlers')
logger.setLevel(level=logging.INFO)


class ToolHandler(ABC):

    def call_function(self, function_name, call_id, args):
        # get method by name if it exists
        meth = getattr(self, function_name)
        # check that method exists
        if meth:
            # call method with args
            return meth(json.loads(args))
        else:
            return f"Unknown Function: {function_name}"
        
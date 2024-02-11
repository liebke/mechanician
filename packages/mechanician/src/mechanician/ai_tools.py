from abc import ABC, abstractmethod
import json
import logging

logger = logging.getLogger(__name__)

class AITools(ABC):

    def call_function(self, function_name, call_id, args):
        # get method by name if it exists
        if hasattr(self, function_name):
            meth = getattr(self, function_name)
            # check that method exists
            if meth:
                if args is None:
                    # call method without args
                    resp = meth(args)
                    if resp is not None:
                        return resp
                elif args.strip():
                    # call method with args
                    resp = meth(json.loads(args))
                    if resp is not None:
                        return resp
                else:
                    resp = meth(args)
                    if resp is not None:
                        return resp
            else:
                return f"Unknown Function: {function_name}"
        
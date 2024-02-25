import json
import logging
from mechanician.ai_tools import AITools
import random
import re

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
logger.addHandler(handler)


def preprocess_string(s):
    # Convert to lowercase, remove punctuation, and split into words
    return re.sub(r'\W+', ' ', s.lower()).split()


def get_closest_match(s, dictionary):
    s_words = set(preprocess_string(s))
    best_match = None
    best_match_score = 0
    for key in dictionary.keys():
        key_words = set(preprocess_string(key))
        # Calculate the Jaccard similarity
        score = len(s_words & key_words) / len(s_words | key_words)
        if score > best_match_score:
            best_match = key
            best_match_score = score
    if best_match is not None:
        return dictionary[best_match]
    else:
        return None
    


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


    def get_weather(self, input: dict):
        location = input.get("location", "unknown")
        date = input.get("date", "unknown")
        if location == "unknown":
            resp = f"location is required."
            logger.info(resp)
            return resp
        
        if date == "unknown":
            resp = f"date is required."
            logger.info(resp)
            return resp
        # read weather_reports from middle_earth_weather.json
        with open("./middle_earth_weather.json", "r") as f:
            weather_reports = json.load(f)
        resp = random.choice(get_closest_match(location, weather_reports).get("reports", []))
        if resp == None:
            resp = f"Location {location} not found."
        logger.info(f"Getting weather for {input}")
        # logger.info(pprint.pformat(resp))
        return resp


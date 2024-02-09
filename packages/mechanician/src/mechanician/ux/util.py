# Import Markdown and Console from rich library for pretty terminal outputs
from rich.markdown import Markdown
import logging

logger = logging.getLogger(__name__)

def print_markdown(console, text):
    console.print(Markdown(text))
    return
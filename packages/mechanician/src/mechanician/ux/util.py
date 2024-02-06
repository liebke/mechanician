# Import Markdown and Console from rich library for pretty terminal outputs
from rich.markdown import Markdown
import logging

logger = logging.getLogger('mechanician.ux.util')
logger.setLevel(level=logging.INFO)


def print_markdown(console, text):
    console.print(Markdown(text))
    return
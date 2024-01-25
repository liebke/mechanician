# Import Markdown and Console from rich library for pretty terminal outputs
from rich.markdown import Markdown


def print_markdown(console, text):
    console.print(Markdown(text))
    return
"""Console script for lid_toolkit."""

import typer
from rich.console import Console

from lid_toolkit import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for lid_toolkit."""
    console.print("Replace this message by putting your code into "
               "lid_toolkit.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()

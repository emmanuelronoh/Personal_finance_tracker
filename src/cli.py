import click
from main import main_menu  # Import the main_menu function from main.py

@click.command()
def cli():
    """Entry point for the Personal Finance Tracker CLI."""
    main_menu()

if __name__ == '__main__':
    cli()

from database import init_db
from cli import cli

def main():
    # Initialize the database
    init_db()
    # Run the CLI
    cli()

if __name__ == '__main__':
    main()

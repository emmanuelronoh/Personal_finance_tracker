import click
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from auth import register_user, login_user, delete_user, recover_password
from transaction import (
    add_transaction, get_transactions, update_transaction, delete_transaction,
    calculate_spending_by_category
)
from budget import add_budget, get_budgets, update_budget, delete_budget
from recurring import (
    add_recurring_transaction, get_recurring_transactions, 
    update_recurring_transaction, delete_recurring_transaction
)
from models import User

# Initialize the database
init_db()

@click.group()
def cli():
    """Personal Finance Tracker CLI."""
    pass

def main_menu():
    """Display the main menu and handle user input."""
    while True:
        click.echo("\nSelect an option:")
        click.echo("1: Login")
        click.echo("2: Register")
        click.echo("3: Delete Account")
        click.echo("4: Exit")

        choice = click.prompt("Enter the number of your choice", type=int)

        if choice == 1:
            login()
        elif choice == 2:
            register()
        elif choice == 3:
            delete_account()
        elif choice == 4:
            click.echo("Exiting...")
            break
        else:
            click.echo("Invalid option. Please try again.")

def register():
    """Register a new user."""
    db = SessionLocal()  
    try:
        username = click.prompt("Your username")
        password = click.prompt("Your password", hide_input=True)
        email = click.prompt("Your email address")
        user = register_user(db, username, password, email)
        click.echo(f'User {user.username} registered successfully!')
    except Exception as e:
        click.echo(f'Error: {e}')
    finally:
        db.close()

def login():
    """Login an existing user."""
    db = SessionLocal()  
    username = click.prompt("Your username")
    password = click.prompt("Your password", hide_input=True)
    user = login_user(db, username, password)

    if user:
        click.echo(f'Welcome back, {user.username}!')
        manage_finances(db, user)
    else:
        click.echo('Error: Invalid username or password.')
        recover = click.prompt("Do you want to recover your password? (yes/no)", type=str).lower()
        if recover == 'yes':
            if recover_password(db, username):
                click.echo("Recovery process initiated. Please check your email.")
            else:
                click.echo("Error: Unable to initiate recovery process.")
    
    db.close()

def manage_finances(db: Session, user: User):
    """Manage finances for the logged-in user."""
    while True:
        click.echo("\nOptions: [1] Manage Transactions [2] Manage Budgets [3] Analyze Spending [4] Manage Recurring Transactions [5] Logout")
        choice = click.prompt("Choose an option", type=int)

        if choice == 1:
            manage_transactions(db, user)
        elif choice == 2:
            manage_budgets(db, user)
        elif choice == 3:
            analyze_spending(db, user)
        elif choice == 4:
            manage_recurring_transactions(db, user)
        elif choice == 5:
            click.echo("Logging out...")
            break
        else:
            click.echo("Invalid option.")

def manage_transactions(db: Session, user: User):
    """Manage transactions."""
    while True:
        click.echo("\nTransaction Options: [1] Add Transaction [2] View Transactions [3] Back")
        trans_choice = click.prompt("Choose an option", type=int)

        if trans_choice == 1:
            amount = click.prompt("Enter transaction amount", type=float)
            category = click.prompt("Enter transaction category")
            add_transaction(db, user.id, amount, category)
            click.echo("Transaction added.")
        elif trans_choice == 2:
            transactions = get_transactions(db, user.id)
            if transactions:
                for txn in transactions:
                    click.echo(f'{txn.date}: {txn.category} - ${txn.amount:.2f}')
            else:
                click.echo("No transactions found.")
        elif trans_choice == 3:
            break  # Go back to the main finance management menu
        else:
            click.echo("Invalid option.")

def manage_budgets(db: Session, user: User):
    """Manage budgets."""
    while True:
        click.echo("\nBudget Options: [1] Set Budget [2] View Budgets [3] Update Budget [4] Delete Budget [5] Back")
        budget_choice = click.prompt("Choose an option", type=int)

        if budget_choice == 1:
            category = click.prompt("Enter budget category")
            limit = click.prompt("Enter budget limit", type=float)
            add_budget(db, user.id, category, limit)
            click.echo("Budget set.")
        elif budget_choice == 2:
            budgets = get_budgets(db, user.id)
            if budgets:
                for budget in budgets:
                    click.echo(f'{budget.id}: {budget.category} - ${budget.limit:.2f}')
            else:
                click.echo("No budgets found.")
        elif budget_choice == 3:
            budgets = get_budgets(db, user.id)
            if budgets:
                budget_id = click.prompt("Enter the ID of the budget to update", type=int)
                new_limit = click.prompt("Enter the new budget limit", type=float)
                updated_budget = update_budget(db, budget_id, new_limit)
                if updated_budget:
                    click.echo(f'Budget updated: {updated_budget.category} - ${updated_budget.limit:.2f}')
                else:
                    click.echo("Error: Budget not found.")
            else:
                click.echo("No budgets available to update.")
        elif budget_choice == 4:
            budgets = get_budgets(db, user.id)
            if budgets:
                budget_id = click.prompt("Enter the ID of the budget to delete", type=int)
                if delete_budget(db, budget_id):
                    click.echo("Budget deleted successfully.")
                else:
                    click.echo("Error: Budget not found.")
            else:
                click.echo("No budgets available to delete.")
        elif budget_choice == 5:
            break  # Go back to the main finance management menu
        else:
            click.echo("Invalid option.")

def analyze_spending(db: Session, user: User):
    """Analyze spending by category."""
    spending_analysis = calculate_spending_by_category(db, user.id)
    click.echo("\nSpending Analysis by Category:")
    for category, total in spending_analysis.items():
        click.echo(f'{category}: ${total:.2f}')

def manage_recurring_transactions(db: Session, user: User):
    """Manage recurring transactions."""
    while True:
        click.echo("\nRecurring Transactions Options: [1] Add [2] View [3] Update [4] Delete [5] Back")
        sub_choice = click.prompt("Choose an option", type=int)

        if sub_choice == 1:
            amount = click.prompt("Enter recurring transaction amount", type=float)
            category = click.prompt("Enter recurring transaction category")
            frequency = click.prompt("Enter frequency (daily, weekly, monthly)")
            next_occurrence = click.prompt("Enter next occurrence date (YYYY-MM-DD)", type=str)
            add_recurring_transaction(db, user.id, category, amount, frequency, next_occurrence)
            click.echo("Recurring transaction added.")
        elif sub_choice == 2:
            recurring_transactions = get_recurring_transactions(db, user.id)
            if recurring_transactions:
                for rtxn in recurring_transactions:
                    click.echo(f'{rtxn.id}: {rtxn.category} - ${rtxn.amount:.2f} (Next: {rtxn.next_occurrence})')
            else:
                click.echo("No recurring transactions found.")
        elif sub_choice == 3:
            recurring_transactions = get_recurring_transactions(db, user.id)
            if recurring_transactions:
                rtxn_id = click.prompt("Enter the ID of the recurring transaction to update", type=int)
                amount = click.prompt("Enter new amount", type=float)
                category = click.prompt("Enter new category")
                frequency = click.prompt("Enter new frequency (daily, weekly, monthly)")
                next_occurrence = click.prompt("Enter new next occurrence date (YYYY-MM-DD)", type=str)
                updated_recurring = update_recurring_transaction(db, rtxn_id, amount, category, frequency, next_occurrence)
                if updated_recurring:
                    click.echo("Recurring transaction updated.")
                else:
                    click.echo("Error: Recurring transaction not found.")
            else:
                click.echo("No recurring transactions available to update.")
        elif sub_choice == 4:
            recurring_transactions = get_recurring_transactions(db, user.id)
            if recurring_transactions:
                rtxn_id = click.prompt("Enter the ID of the recurring transaction to delete", type=int)
                if delete_recurring_transaction(db, rtxn_id):
                    click.echo("Recurring transaction deleted.")
                else:
                    click.echo("Error: Recurring transaction not found.")
            else:
                click.echo("No recurring transactions available to delete.")
        elif sub_choice == 5:
            break  # Go back to the main finance management menu
        else:
            click.echo("Invalid option.")

def delete_account():
    """Delete a user account."""
    db = SessionLocal()
    username = click.prompt("Enter your username")
    if delete_user(db, username):
        click.echo(f'Account {username} deleted successfully.')
    else:
        click.echo('Error: Account not found.')
    db.close()

if __name__ == '__main__':
    main_menu()

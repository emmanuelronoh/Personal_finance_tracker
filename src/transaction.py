from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Transaction, RecurringTransaction  # Import models for transactions
import matplotlib.pyplot as plt
from datetime import datetime

def add_transaction(db: Session, user_id: int, amount: float, category: str):
    """Add a new transaction for the user."""
    # Create a new Transaction instance
    transaction = Transaction(amount=amount, category=category, user_id=user_id)
    # Add the transaction to the session
    db.add(transaction)
    # Commit the session to save the transaction to the database
    db.commit()
    # Refresh the transaction instance to get the updated data from the database
    db.refresh(transaction)
    return transaction

def get_transactions(db: Session, user_id: int):
    """Retrieve all transactions for the user."""
    # Query to get all transactions for a specific user
    return db.query(Transaction).filter(Transaction.user_id == user_id).all()

def update_transaction(db: Session, transaction_id: int, amount: float, category: str):
    """Update an existing transaction."""
    # Find the transaction by its ID
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction:
        # Update the transaction's amount and category
        transaction.amount = amount
        transaction.category = category
        # Commit the session to save changes
        db.commit()
        return transaction
    return None

def delete_transaction(db: Session, transaction_id: int):
    """Delete a transaction."""
    # Find the transaction by its ID
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction:
        # Delete the transaction from the session
        db.delete(transaction)
        # Commit the session to apply changes
        db.commit()
        return True
    return False

def calculate_spending_by_category(db: Session, user_id: int):
    """Calculate total spending by category for a user."""
    # Query to sum the total amount spent by category for a specific user
    spending = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')  # Use SQL aggregation to get totals
    ).filter(Transaction.user_id == user_id).group_by(Transaction.category).all()
    
    # Return a dictionary with category as key and total spent as value
    return {category: total for category, total in spending}

def calculate_spending_over_time(db: Session, user_id: int, start_date: datetime, end_date: datetime):
    """Calculate total spending within a specific date range."""
    # Query to sum the total amount spent between start and end dates
    spending = db.query(func.sum(Transaction.amount).label('total')).filter(
        Transaction.user_id == user_id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar()
    
    return spending or 0  # Return 0 if no spending found

def plot_spending_by_category(spending_data):
    """Plot spending data as a bar chart."""
    # Prepare data for plotting
    categories = list(spending_data.keys())
    amounts = list(spending_data.values())

    # Create a bar chart for spending by category
    plt.bar(categories, amounts)
    plt.xlabel('Category')
    plt.ylabel('Total Spending')
    plt.title('Spending by Category')
    plt.xticks(rotation=45)
    plt.tight_layout()  # Adjust layout for better display
    plt.show()

def check_budget_exceedance(db: Session, user_id: int, budgets):
    """Check if the user has exceeded their budget."""
    # Get total spending by category for the user
    spending = calculate_spending_by_category(db, user_id)

    alerts = []
    # Compare each budget with spending
    for budget in budgets:
        spent = spending.get(budget.category, 0)  # Get spent amount for the category
        if spent > budget.limit:  # Check if spending exceeds the limit
            alerts.append(f"Alert: You have exceeded your budget for {budget.category} by ${spent - budget.limit:.2f}")

    return alerts

# Recurring Transactions Functions

def add_recurring_transaction(db: Session, user_id: int, amount: float, category: str, frequency: str, next_occurrence: str):
    """Add a new recurring transaction."""
    # Create a new RecurringTransaction instance
    recurring_transaction = RecurringTransaction(
        user_id=user_id,
        amount=amount,
        category=category,
        frequency=frequency,
        next_occurrence=datetime.strptime(next_occurrence, '%Y-%m-%d')  # Parse the next occurrence date
    )
    db.add(recurring_transaction)
    db.commit()
    db.refresh(recurring_transaction)
    return recurring_transaction

def get_recurring_transactions(db: Session, user_id: int):
    """Retrieve all recurring transactions for the user."""
    # Query to get all recurring transactions for a specific user
    return db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id).all()

def update_recurring_transaction(db: Session, transaction_id: int, amount: float, category: str, frequency: str, next_occurrence: str):
    """Update an existing recurring transaction."""
    # Find the recurring transaction by its ID
    recurring_transaction = db.query(RecurringTransaction).filter(RecurringTransaction.id == transaction_id).first()
    if recurring_transaction:
        # Update the transaction's attributes
        recurring_transaction.amount = amount
        recurring_transaction.category = category
        recurring_transaction.frequency = frequency
        recurring_transaction.next_occurrence = datetime.strptime(next_occurrence, '%Y-%m-%d')  # Parse new date
        db.commit()
        return recurring_transaction
    return None

def delete_recurring_transaction(db: Session, transaction_id: int):
    """Delete a recurring transaction."""
    # Find the recurring transaction by its ID
    recurring_transaction = db.query(RecurringTransaction).filter(RecurringTransaction.id == transaction_id).first()
    if recurring_transaction:
        # Delete the transaction from the session
        db.delete(recurring_transaction)
        db.commit()
        return True
    return False

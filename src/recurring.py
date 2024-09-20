from sqlalchemy.orm import Session
from models import RecurringTransaction
from datetime import datetime

def add_recurring_transaction(db: Session, user_id: int, category: str, amount: float, frequency: str, next_occurrence: str):
    """Add a new recurring transaction."""
    recurring_transaction = RecurringTransaction(
        user_id=user_id,
        category=category,
        amount=amount,
        frequency=frequency,
        next_occurrence=datetime.strptime(next_occurrence, "%Y-%m-%d")  # Convert string to datetime
    )
    db.add(recurring_transaction)
    db.commit()
    db.refresh(recurring_transaction)
    return recurring_transaction

def get_recurring_transactions(db: Session, user_id: int):
    """Retrieve all recurring transactions for the user."""
    return db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id).all()

def update_recurring_transaction(db: Session, transaction_id: int, amount: float, category: str, frequency: str, next_occurrence: str):
    """Update an existing recurring transaction."""
    recurring_transaction = db.query(RecurringTransaction).filter(RecurringTransaction.id == transaction_id).first()
    if recurring_transaction:
        recurring_transaction.amount = amount
        recurring_transaction.category = category  # Updated to allow category change
        recurring_transaction.frequency = frequency
        recurring_transaction.next_occurrence = datetime.strptime(next_occurrence, "%Y-%m-%d")  # Update next_occurrence
        db.commit()
        return recurring_transaction
    return None

def delete_recurring_transaction(db: Session, transaction_id: int):
    """Delete a recurring transaction."""
    recurring_transaction = db.query(RecurringTransaction).filter(RecurringTransaction.id == transaction_id).first()
    if recurring_transaction:
        db.delete(recurring_transaction)
        db.commit()
        return True
    return False

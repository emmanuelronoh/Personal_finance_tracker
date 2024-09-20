from sqlalchemy.orm import Session
from models import Budget, RecurringTransaction  # Updated to use RecurringTransaction

def add_budget(db: Session, user_id: int, category: str, limit: float):
    """Add a budget for a user."""
    budget = Budget(category=category, limit=limit, user_id=user_id)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget

def get_budgets(db: Session, user_id: int):
    """Retrieve all budgets for the user."""
    return db.query(Budget).filter(Budget.user_id == user_id).all()

def update_budget(db: Session, budget_id: int, limit: float):
    """Update an existing budget."""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if budget:
        budget.limit = limit
        db.commit()
        return budget
    return None

def delete_budget(db: Session, budget_id: int):
    """Delete a budget."""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if budget:
        db.delete(budget)
        db.commit()
        return True
    return False

def get_budget_summary(db: Session, user_id: int):
    """Get a summary of budgets for the user."""
    budgets = get_budgets(db, user_id)
    total_budget = sum(budget.limit for budget in budgets)
    return {
        'total_budget': total_budget,
        'budgets': budgets
    }

# Recurring Transactions Functions

def add_recurring_transaction(db: Session, user_id: int, category: str, amount: float, frequency: str):
    """Add a new recurring transaction."""
    recurring_transaction = RecurringTransaction(
        user_id=user_id,
        category=category,
        amount=amount,
        frequency=frequency,
        next_occurrence=None  # Set initial next_occurrence as needed
    )
    db.add(recurring_transaction)
    db.commit()
    db.refresh(recurring_transaction)
    return recurring_transaction

def get_recurring_transactions(db: Session, user_id: int):
    """Retrieve all recurring transactions for the user."""
    return db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id).all()

def update_recurring_transaction(db: Session, transaction_id: int, amount: float, frequency: str):
    """Update an existing recurring transaction."""
    recurring_transaction = db.query(RecurringTransaction).filter(RecurringTransaction.id == transaction_id).first()
    if recurring_transaction:
        recurring_transaction.amount = amount
        recurring_transaction.frequency = frequency
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

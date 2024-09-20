from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)  # Unique identifier for each user
    username = Column(String, unique=True, index=True)  # Unique username for login
    password_hash = Column(String)  # Hashed password for user authentication
    email = Column(String, unique=True, index=True)  # Unique email for notifications and recovery

    # Relationships to other models
    transactions = relationship('Transaction', back_populates='user')  # User's transactions
    budgets = relationship('Budget', back_populates='user')  # User's budgets
    recurring_transactions = relationship('RecurringTransaction', back_populates='user')  # User's recurring transactions

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)  # Unique identifier for each transaction
    amount = Column(Float)  # Amount of the transaction
    category = Column(String)  # Category of the transaction (e.g., food, bills)
    date = Column(DateTime, default=datetime.utcnow)  # Timestamp of the transaction
    user_id = Column(Integer, ForeignKey('users.id'))  # Foreign key linking to the user

    # Relationship back to the user
    user = relationship('User', back_populates='transactions')

class Budget(Base):
    __tablename__ = 'budgets'
    id = Column(Integer, primary_key=True)  # Unique identifier for each budget
    category = Column(String)  # Category of the budget
    limit = Column(Float)  # Spending limit for the budget
    user_id = Column(Integer, ForeignKey('users.id'))  # Foreign key linking to the user

    # Relationship back to the user
    user = relationship('User', back_populates='budgets')

class RecurringTransaction(Base):
    __tablename__ = 'recurring_transactions'
    id = Column(Integer, primary_key=True)  # Unique identifier for each recurring transaction
    user_id = Column(Integer, ForeignKey('users.id'))  # Foreign key linking to the user
    amount = Column(Float)  # Amount for the recurring transaction
    category = Column(String)  # Category of the recurring transaction
    frequency = Column(String)  # Frequency of the transaction (e.g., daily, weekly, monthly)
    next_occurrence = Column(DateTime)  # Next scheduled date for the transaction

    # Relationship back to the user
    user = relationship('User', back_populates='recurring_transactions')

def get_budget_summary(user):
    """Summarize budgets and spending for a user.

    Args:
        user: The user object whose budget summary is to be generated.

    Returns:
        A dictionary containing budget limits and amounts spent for each category.
    """
    budgets = {b.category: b.limit for b in user.budgets}  # Dictionary of category: limit
    total_spent = {c: 0 for c in budgets.keys()}  # Initialize spending tracker for each category

    # Calculate total spending from transactions
    for transaction in user.transactions:
        total_spent[transaction.category] += transaction.amount  # Sum amounts for each category

    # Calculate expected spending from recurring transactions
    for recurring in user.recurring_transactions:
        if recurring.frequency == 'monthly':
            total_spent[recurring.category] += recurring.amount  # Add recurring amount based on frequency

    # Prepare summary with limits and spent amounts
    return {cat: {"limit": budgets[cat], "spent": total_spent[cat]} for cat in budgets}

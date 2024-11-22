from application import Application 
from domain import Transaction
from repositories import SQLiteTransactionRepository

if __name__ == "__main__":
    # Initialize SQLite repository
    sqlite_repo = SQLiteTransactionRepository("transactions.db")

    # Create the application
    app = Application(sqlite_repo)

    # Add a few transactions
    app.add_transaction(100.0, "2024-11-22", "Groceries")
    app.add_transaction(200.0, "2024-11-21", "Rent payment")

    # List all transactions
    print("\nAll Transactions:")
    app.list_transactions()

    # Find a transaction by ID
    print("\nFind Transaction:")
    app.find_transaction(1)

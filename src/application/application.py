from ..domain.transaction import Transaction
from ..repositories import SQLiteTransactionRepository

class Application:
    def __init__(self, repository: SQLiteTransactionRepository):
        self.repository = repository

    def add_transaction(self, amount: float, date: str, description: str, category: str, notes: str) -> None:
        '''Adds a transaction to database.'''
        transaction = Transaction(None, amount, date, description, category.upper(), notes)
        self.repository.add_transaction(transaction)
        print(f"Transaction added: {transaction}")

    def list_transactions(self):
        '''Gets all transactions'''
        transactions = self.repository.get_all_transactions()
        for transaction in transactions:
            print(transaction)

    def find_transaction(self, transaction_id: int):
        '''Returns a transaction given the id'''
        transaction = self.repository.find_transaction_by_id(transaction_id)
        if transaction:
            print(f"Transaction found: {transaction}")
        else:
            print(f"No transaction found with ID {transaction_id}")

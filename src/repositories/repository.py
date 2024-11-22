from typing import Optional, List

from ..domain.transaction.py import Transaction

class TransactionRepository:
    def __init__(self):
        self.transactions = []

    def add(self, transaction: Transaction):
        '''Creates a new transaction'''
        self.transactions.append(transaction)

    def get_all(self) -> List[Transaction]:
        '''Gets all transactions'''
        return self.transactions

    def find_by_id(self, transaction_id: int) -> Optional[Transaction]:
        '''Returns a transaction by transaction id'''
        return next((t for t in self.transactions if t.transaction_id == transaction_id), None)

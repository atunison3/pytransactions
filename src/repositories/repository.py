from typing import Optional, List

from domain.transaction import Transaction

class TransactionRepository:
    def __init__(self):
        self.transactions = []

    def create(self, transaction: Transaction):
        '''Creates a new transaction'''
        self.transactions.append(transaction)

    def read_all(self) -> List[Transaction]:
        '''Gets all transactions'''
        return self.transactions

    def read_by_id(self, transaction_id: int) -> Optional[Transaction]:
        '''Returns a transaction by transaction id'''
        return next((t for t in self.transactions if t.transaction_id == transaction_id), None)

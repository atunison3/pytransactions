import sqlite3

from domain.transaction import Transaction

class SQLiteTransactionRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        '''Initializes the database'''
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    date DATE NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    notes TEXT
                )
            ''')
            conn.commit()

    def add_transaction(self, transaction):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions 
                    (amount, date, description, category, notes)
                VALUES 
                    (?, ?, ?, ?, ?)
            ''', (transaction.amount, transaction.date, transaction.description))
            conn.commit()
            transaction.transaction_id = cursor.lastrowid

    def get_all_transactions(self) -> [Transaction]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, amount, date, description category, notes FROM transactions')
            rows = cursor.fetchall()
            return [Transaction(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]

    def find_transaction_by_id(self, transaction_id: int) -> Transaction:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, amount, date, description category, notes FROM transactions WHERE id = ?', 
                (transaction_id,))
            row = cursor.fetchone()
            if row:
                return Transaction(row[0], row[1], row[2], row[3], row[4], row[5])
            return None

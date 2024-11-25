import sqlite3

try:
    from domain.transaction import Transaction 
    from domain.category import Category
    from domain.recurring_expense import RecurringExpense
except ModuleNotFoundError:
    from ..domain.transaction import Transaction
    from ..domain.category import Category
    from ..domain.recurring_expense import RecurringExpense

class SQLiteTransactionRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        #self._initialize_database()

    def _initialize_database(self):
        '''Initializes the database'''
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create transactions table
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

            # Create categories table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                monthly_allocation REAL NOT NULL,
                notes TEXT
            );
            ''')

            # Create recurring expenses table
            cursor.execute('''
            CREATE TABLE recurring_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each expense
                amount REAL NOT NULL,                 -- Expense amount
                frequency TEXT NOT NULL,              -- Frequency (e.g., "daily", "weekly", "monthly", "yearly")
                category TEXT NOT NULL REFERENCES categories(description), 
                description TEXT NOT NULL,            -- Short description of the expense
                notes TEXT,                           -- Additional notes (optional)
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- Timestamp of when the expense was added
            );
            ''')
            
            conn.commit()

    def create_transaction(self, transaction: Transaction):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions 
                    (amount, date, description, category, notes)
                VALUES 
                    (?, ?, ?, ?, ?)
            ''', (transaction.amount, transaction.date, transaction.description, transaction.category, transaction.notes))
            conn.commit()
            #transaction.transaction_id = cursor.lastrowid

    def create_category(self, category: Category):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO categories 
                    (description, monthly_allocation, notes)
                VALUES
                    (?, ?, ?)
                ''',
                (category.description, category.monthly_allocation, category.notes))
            conn.commit()
            #category.category_id = cursor.lastrowid

    def create_recurring_expense(self, re: RecurringExpense):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recurring_expenses
                    (amount, frequency, category, description, notes)
                VALUES
                    (?, ?, ?, ?, ?)
                ''',
                (re.amount, re.frequency, re.category, re.description, re.notes))
            conn.commit()
            #re.recurring_expense_id = cursor.lastrowid

    def read_all_transactions(self) -> [Transaction]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, amount, date, description, category, notes FROM transactions;')
            rows = cursor.fetchall()
            return [Transaction(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]

    def read_all_recurring_expenses(self) -> [RecurringExpense]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM recurring_expenses;')
            rows = cursor.fetchall()
            return [RecurringExpense(*row) for row in rows]

    def read_transaction_by_id(self, transaction_id: int) -> Transaction:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, amount, date, description, category, notes FROM transactions WHERE id = ?', 
                (transaction_id,))
            row = cursor.fetchone()
            if row:
                return Transaction(row[0], row[1], row[2], row[3], row[4], row[5])
            return None

    def read_last_seven_days(self) -> [Transaction]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * 
                FROM transactions
                WHERE DATE(date) >= DATE('now', '-7 days')
                  AND DATE(date) <= DATE('now')
                ORDER BY date DESC;
                '''
            )
            rows = cursor.fetchall()
            return [Transaction(*row) for row in rows]

    def read_current_month_transactions(self) -> [Transaction]:
        with sqlite3.connect(self.db_path) as conn: 
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT *
                FROM transactions
                WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
                ORDER BY date DESC;
                '''
            )
            rows = cursor.fetchall()
            return [Transaction(*row) for row in rows]

    def read_all_categories(self) -> [Category]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor() 
            cursor.execute('SELECT * FROM categories;')
            rows = cursor.fetchall()
            return [Category(*row) for row in rows]

    def update_transaction(self, t: Transaction) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor() 
            cursor.execute(
                '''
                UPDATE transactions 
                SET amount=?, date=?, description=?, category=?, notes=?
                WHERE id=?
                RETURNING id, amount, date, description, category, notes
                ''',
                (t.amount, t.date, t.description, t.category, t.notes, t.transaction_id)
            )
            t = cursor.fetchone()

            conn.commit()
            
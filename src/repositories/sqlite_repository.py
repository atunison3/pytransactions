import sqlite3

try:
    from domain.transaction import Transaction
    from domain.category import Category
    from domain.recurring_expense import RecurringExpense
    from domain.user import User
except ModuleNotFoundError:
    from ..domain.transaction import Transaction
    from ..domain.category import Category
    from ..domain.recurring_expense import RecurringExpense
    from ..domain.user import User

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

    def create_user(self, user: User):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO users 
                    (username, password)
                VALUES 
                    (?, ?)
                ''',
                (user.username, user.password)
            )
            conn.commit()

    def create_transaction(self, transaction: Transaction):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions 
                    (amount, date, description, category, notes, subcategory)
                VALUES 
                    (?, ?, ?, ?, ?, ?)
            ''', (transaction.amount, transaction.date, transaction.description, transaction.category, transaction.notes, transaction.subcategory))
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

    def query_transactions(self, start_date: str, end_date: str, category: str, description: str):
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category:
            query += " AND category = ?"
            params.append(category)
        if description:
            query += " AND description LIKE ?"
            params.append(f"%{description}%")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall() 
            return [Transaction(*row) for row in rows]

    def read_all_transactions(self) -> [Transaction]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM transactions;')
            rows = cursor.fetchall()
            return [Transaction(*row) for row in rows]

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
                'SELECT * FROM transactions WHERE id = ?', 
                (transaction_id,))
            row = cursor.fetchone()
            if row:
                return Transaction(*row)
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

    def read_user_by_username(self, username: str) -> User:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * 
                FROM users 
                WHERE username = ?;
                ''',
                (username,)
            )
            rows = cursor.fetchone()
            return User(*rows)

    def update_transaction(self, t: Transaction) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor() 
            cursor.execute(
                '''
                UPDATE transactions 
                SET amount=?, date=?, description=?, category=?, notes=?, subcategory=?
                WHERE id=?
                RETURNING id, amount, date, description, category, notes, subcategory
                ''',
                (t.amount, t.date, t.description, t.category, t.notes, t.subcategory, t.transaction_id)
            )
            t = cursor.fetchone()

            conn.commit()

    def delete_transaction(self, transaction_id: int):
        '''Deletes a transaction'''
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ?;', (transaction_id,))
            conn.commit()  
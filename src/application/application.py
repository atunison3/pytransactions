from passlib.context import CryptContext

try:
    from domain import Transaction, Category, RecurringExpense, User
    from repositories import SQLiteTransactionRepository
except ModuleNotFoundError:
    from ..domain.transaction import Transaction
    from ..domain.category import Category 
    from ..domain.recurring_expense import RecurringExpense
    from ..domain.user import User
    from ..repositories.sqlite_repository import SQLiteTransactionRepository

# --- Password hashing context ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Application:
    def __init__(self, repository: SQLiteTransactionRepository):
        self.repository = repository

    def get_user_by_username(self, username: str) -> User:
        return self.repository.read_user_by_username(username)

    def create_user(self, username: str, password: str):
        '''Creates a user in database'''

        # Hash user password
        hashed_password = pwd_context.hash(password)

        # Create user entity
        user = User(None, username, hashed_password)

        self.repository.create_user(user)

    def create_transaction(self, amount: float, date: str, description: str, category: str, subcategory: str, notes: str) -> None:
        '''Adds a transaction to database.'''

        # Correct the category
        description = description.strip()
        category = category.title().strip()
        if subcategory:
            subcategory = subcategory.strip()
        if notes:
            notes = notes.strip()

        transaction = Transaction(None, amount, date, description, category.title(), notes, subcategory)
        self.repository.create_transaction(transaction)

    def create_category(self, description: str, monthly_allocation: float, notes: str) -> None:
        '''Adds a category to database'''

        # Data integrity check
        description = description.title() 

        category = Category(None, description, monthly_allocation, notes)
        self.repository.create_category(category)
        print(f"\033[92mCategory created: {category}\033[0m")

    def create_recurring_expense(
        self, amount: float, frequency: str, category: str, 
        description: str, notes: str) -> None:
        
        # Data integrity check
        category = category.title()

        # Create recurring expense
        recurring_expense = RecurringExpense(None, amount, frequency, category, description, notes, None)
        self.repository.create_recurring_expense(recurring_expense)

    def list_transactions_from_dashboard(
        self, 
        start_date: str = None, 
        end_date: str = None, 
        category: str = None, 
        description: str = None) -> [Transaction]:
        
        return self.repository.query_transactions(start_date, end_date, category, description)

    def list_transactions(self):
        '''Gets all transactions'''
        transactions = self.repository.read_all_transactions()
        print('\033[92m\nTransactions:\n--------------------------------\033[0m')
        for transaction in transactions:
            print(transaction)

    def list_last_seven_days(self):
        '''Gets last seven days of transactions.'''
        return self.repository.read_last_seven_days()

    def list_categories(self) -> [Category]:
        return self.repository.read_all_categories()

    def list_current_month(self) -> [Transaction]:
        return self.repository.read_current_month_transactions()

    def list_all_recurring(self) ->[RecurringExpense]:
        return self.repository.read_all_recurring_expenses()

    def find_transaction(self, transaction_id: int):
        '''Returns a transaction given the id'''
        transaction = self.repository.read_transaction_by_id(transaction_id)
        return transaction 

    def correct_transaction(self, transaction_id: int, amount: float, date: str, description: str, category: str, subcategory: str, notes: str) -> None:
        '''Updates a transaction'''

        # Correct the category 
        category = category.title()

        # Create a transaction
        transaction = Transaction(transaction_id, amount, date, description, category, notes, subcategory)

        self.repository.update_transaction(transaction)

    def delete_transaction(self, transaction_id: int):
        '''Deletes transaction'''
        self.repository.delete_transaction(transaction_id)

    def print_test_statement(self):
        return '\033[92mWorking!\033[0m'

if __name__=='__main__':
    app = Application()
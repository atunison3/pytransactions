from application import Application 
from repositories import SQLiteTransactionRepository

if __name__ == "__main__":
    # Initialize SQLite repository
    sqlite_repo = SQLiteTransactionRepository("transactions.db")

    # Create the application
    app = Application(sqlite_repo)

    while True:
        print('')
        print(" 0. Quit Application")
        print(" 1. Add transaction")
        print(' 2. Read all transactions')
        print(' 3. Read transaction by id')
        print(' 4. Update transaction')
        print('')

        resp = input("Enter action: ")

        if resp == '0':
            print('Closing application\n')
            break
        elif resp == '1':
            print('Add a transaction\n')
            amount = input('Enter amount:            ')
            date =   input('Enter date [YYYY-MM-DD]: ')
            desc =   input('Enter description:       ')
            cat =    input('Enter category:          ')
            notes =  input('Enter notes:             ')

            # Add transaction
            try:
                # Convert dtypes
                amount = float(amount)
                app.create_transaction(amount, date, desc, cat, notes)

                # Print closing statement
                print('\033[92mSuccessfully added transaction\033[0m')
            except Exception as e:
                print(f'\033[91mFailed to add transaction:\n    {e}\033[0m')

        elif resp == '2':
            app.list_transactions()

        elif resp == '3':
            try:
                # Get transaction id
                transaction_id = int(input('Enter transaction id: '))

                app.find_transaction(transaction_id)
            except Exception as e:
                print(f'\033[91mFailed to read transaction:\n {e}\033[0m')
        elif resp == '4':
            # Get transaction id for transaction to update
            transaction_id = int(input('Enter transaction id to update: '))

            # Get transaction
            transaction = app.find_transaction(transaction_id)

            # Print info and get updates
            print(f'Transcation id: {transaction.transaction_id}')
            transaction.transaction_id = int(input('Enter id: '))
            print(f'Old Date: {transaction.date}')
            transaction.date = input('Enter date: ')
            print(f'Old Amount: ${transaction.amount}')
            transaction.amount = float(input('Enter amount: '))
            print(f'Old Description: {transaction.description}')
            transaction.description = input('Enter description: ')
            print(f'Old Category: {transaction.category}')
            transaction.category = input('Enter category: ')
            print(f'Old Notes: {transaction.notes}')
            transaction.notes = input('Enter notes: ')


            app.correct_transaction(
                transaction.transaction_id, transaction.amount, 
                transaction.date, transaction.description, 
                transaction.category, transaction.notes
            )

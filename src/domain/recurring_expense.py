class RecurringExpense:
    def __init__(
        self, recurring_expense_id: int, 
        amount: float, frequency: str, 
        category: str, description: str, 
        notes: str, created_at: str
    ):
        self.recurring_expense_id = recurring_expense_id 
        self.amount = amount 
        self.frequency = frequency 
        self.category = category 
        self.description = description 
        self.notes = notes 
        self.created_at = created_at 

    def __repr__(self):
        return f'{self.description}: ${self.amount:.2f}'
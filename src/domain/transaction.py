class Transaction:
    def __init__(
        self, transaction_id: int | None, amount: float, date: str, description: str, 
        category: str, notes: str, subcategory: str
    ):
        self.transaction_id = transaction_id
        self.amount = amount
        self.date = date
        self.description = description
        self.category = category
        self.notes = notes 
        self.subcategory = subcategory

    def __repr__(self):
        return f"Transaction(id={self.transaction_id}, amount={self.amount}, date='{self.date}', description='{self.description}', category='{self.category}', notes='{self.notes}', subcategory='{self.subcategory}')"

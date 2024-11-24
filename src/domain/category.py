class Category:
    def __init__(self, category_id: int, description: str, monthly_allocation: float, notes: str):
        self.category_id = category_id
        self.description = description 
        self.monthly_allocation = monthly_allocation 
        self.notes = notes 

    def __repr__(self):
        return f'{self.description}: ${self.monthly_allocation:.2f}'
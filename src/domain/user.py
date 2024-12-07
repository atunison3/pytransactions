class User:
    def __init__(self, user_id: int, username: str, password: str):
        self.user_id = user_id, 
        self.username = username 
        self.password = password 

    def __repr__(self):
        return f'{self.user_id}. {self.username}'
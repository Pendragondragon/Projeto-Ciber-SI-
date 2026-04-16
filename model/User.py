class User:
    def __init__(self, id, username, email, palavrapass):
        self.id = id
        self.username = username
        self.email = email
        self.palavrapass = palavrapass

    def __str__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
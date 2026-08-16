class User:

    def __init__(self, id, username, password, role):

        self.id = id
        self.username = username
        self.password = password
        self.role = role


    def to_dict(self):

        return {
            "id": self.id,
            "username": self.username,
            "role": self.role
        }
from auth.repository import AuthRepository


class AuthService:
    def __init__(self):
        self.repository = AuthRepository()


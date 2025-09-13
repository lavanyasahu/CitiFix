import bcrypt
from database import Database

class Authentication:
    def __init__(self):
        self.db = Database()

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password, hashed):
        if not password or not hashed:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    def login_user(self, username, password):
        user = self.db.get_user_by_username(username)
        if not user:
            return None
        if self.verify_password(password, user['password_hash']):
            u = dict(user)
            u.pop('password_hash', None)
            return u
        return None

    def register_citizen(self, username, email, password, phone=None):
        pwd = self.hash_password(password)
        return self.db.create_user(username, email, pwd, phone, role='citizen')

    def create_authority(self, username, email, password, phone=None):
        pwd = self.hash_password(password)
        return self.db.create_user(username, email, pwd, phone, role='authority')

    def create_admin_user(self, username, email, password, phone=None):
        pwd = self.hash_password(password)
        return self.db.create_user(username, email, pwd, phone, role='admin')

from constants import DEBUG

LOGGED_OUT=0
LOGGED_IN=0


class UserManager:
    _instance = None
    _current_user = None

    class _User:
        def __init__(self, username, role):
            self.username = username
            self.role = role
            self.state = LOGGED_OUT

        def login(self):
            self.state = LOGGED_IN

        def logout(self):
            self.state = LOGGED_OUT

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserManager, cls).__new__(cls)
            cls._instance.users = {}
        return cls._instance

    def create_user(self, username, role):
        if username not in self.users:
            self.users[username] = self._User(username, role)
            if DEBUG:
                print(f"User '{username}' created with role '{role}'.")
        else:
            if DEBUG:
                print(f"User '{username}' already exists.")

    def login(self, username):
        user = self.users.get(username)
        if user:
            self._current_user=username
            user.login()
            if DEBUG:
                print(f"User '{username}' logged in.")
        else:
            if DEBUG:
                print(f"User '{username}' not found.")

    def logout(self, username):
        user = self.users.get(username)
        if user:
            user.logout()
            if DEBUG:
                print(f"User '{username}' logged out.")
        else:
            if DEBUG:
                print(f"User '{username}' not found.")

    def get_user_state(self, username):
        user = self.users.get(username)
        if user:
            return user.state
        return None
    
    def get_user_info(self, username):
        user = self.users.get(username)
        if user:
            return {
                "username": user.username,
                "role": user.role,
                "state": user.state
            }
        return None

    def user_exists(self, username):
        return username in self.users
    
    def get_current(self):
        return self._current_user
    

UserCollection: UserManager =None

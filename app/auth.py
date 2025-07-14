import json
import hashlib
import os

USERS_FILE = 'data/users.json'

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_users_file():
    if not os.path.exists(USERS_FILE):
        print("Inicializando archivo de usuarios por defecto...")
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        default_password = hash_pass("admin")
        default_data = {
            "admin": {
                "password": default_password,
                "must_change": True
            }
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(default_data, f, indent=4)

def load_users():
    init_users_file()  # Garantiza que siempre esté inicializado
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def check_login(user, password):
    users = load_users()
    return user in users and users[user]['password'] == hash_pass(password)

def must_change_password(user):
    users = load_users()
    return users.get(user, {}).get('must_change', False)

def change_password(user, new_password):
    users = load_users()
    users[user]['password'] = hash_pass(new_password)
    users[user]['must_change'] = False
    save_users(users)

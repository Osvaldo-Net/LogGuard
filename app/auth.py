import json
import hashlib

USERS_FILE = '/app/data/users.json'

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, 'w') as f:
        json.dump(data, f)

def check_login(user, password):
    users = load_users()
    return user in users and users[user]['password'] == hash_pass(password)

def must_change_password(user):
    users = load_users()
    return users[user]['must_change']

def change_password(user, new_password):
    users = load_users()
    users[user]['password'] = hash_pass(new_password)
    users[user]['must_change'] = False
    save_users(users)

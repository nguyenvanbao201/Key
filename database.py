import json
import os

USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"

def load_data(file):
    if not os.path.exists(file):
        with open(file, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_users():
    return load_data(USERS_FILE)

def save_users(data):
    save_data(USERS_FILE, data)

def get_orders():
    return load_data(ORDERS_FILE)

def save_orders(data):
    save_data(ORDERS_FILE, data)

def get_keys():
    return load_data(KEYS_FILE)

def save_keys(data):
    save_data(KEYS_FILE, data)
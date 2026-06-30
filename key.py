import random
import string
import json
from datetime import datetime, timedelta

def create_key(tool):
    chars = string.ascii_uppercase + string.digits

    part1 = ''.join(random.choice(chars) for _ in range(4))
    part2 = ''.join(random.choice(chars) for _ in range(4))
    part3 = ''.join(random.choice(chars) for _ in range(4))
    part4 = ''.join(random.choice(chars) for _ in range(4))

    return f"{tool.upper()}-{part1}-{part2}-{part3}-{part4}"

def get_expire(days):
    return (datetime.now() + timedelta(days=int(days))).strftime("%d/%m/%Y %H:%M:%S")

def get_key(tool, day):

    with open("keys.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if tool not in data:
        return None

    if day not in data[tool]:
        return None

    if len(data[tool][day]) == 0:
        return None

    return data[tool][day][0]

def remove_key(tool, day, key):

    with open("keys.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if key in data[tool][day]:
        data[tool][day].remove(key)

    with open("keys.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
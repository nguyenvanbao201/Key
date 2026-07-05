import random
import string
from datetime import datetime, timedelta

def generate_key(prefix="VB"):
    chars = string.ascii_uppercase + string.digits
    parts = [
        "".join(random.choice(chars) for _ in range(4))
        for _ in range(4)
    ]
    return f"{prefix}-" + "-".join(parts)

def get_expire_time(days=1):
    return (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
from flask import Flask, redirect, request
from database import conn, cursor
from key import get_expire_time
from telegraph_api import create_key_page
import random
import string
import requests


ACCESS_TOKEN = "829b74b1920c6338f83418830e90b0b0caf879fa906b026f3890f7b3f4f5"

app = Flask(__name__)

def create_telegraph_page(key):
    url = "https://api.telegra.ph/createPage"

    content = f'''[
        {{
            "tag":"h3",
            "children":["VBTool Key"]
        }},
        {{
            "tag":"p",
            "children":["Key của bạn: {key}"]
        }}
    ]'''

    data = {
        "access_token": ACCESS_TOKEN,
        "title": "VBTool Key",
        "author_name": "VBTool",
        "content": content,
        "return_content": False
    }

    try:
        r = requests.post(url, data=data).json()

        if r.get("ok"):
            return "https://telegra.ph/" + r["result"]["path"]

        print(r)
        return None

    except Exception as e:
        print(e)
        return None

def create_key():
    chars = string.ascii_uppercase + string.digits
    return "VB-" + "-".join(
        "".join(random.choice(chars) for _ in range(4))
        for _ in range(4)
    )

@app.route("/")
def home():
    return "VBTool API Online"

@app.route("/create")
def create():
    key = create_key()

    # Lưu key vào database
    cursor.execute(
        "INSERT INTO keys(key, device_id, key_type) VALUES (?, ?, ?)",
        (key, "", "FREE")
    )
    conn.commit()

    telegraph = create_telegraph_page(key)

    if telegraph:
        return redirect(telegraph)

    return "Không tạo được Telegraph"

@app.route("/verify")
def verify():
    key = request.args.get("key")
    device = request.args.get("device")

    if not key:
        return {
            "success": False,
            "message": "Thiếu key"
        }

    cursor.execute(
        "SELECT key, device_id, key_type, expire_time FROM keys WHERE key=?",
        (key,)
    )

    row = cursor.fetchone()

    if row is None:
        return {
            "success": False,
            "message": "Key không tồn tại"
        }

    # Nếu key chưa gắn thiết bị thì gắn lần đầu
    if row[1] == "" and device:
        cursor.execute(
            "UPDATE keys SET device_id=? WHERE key=?",
            (device, key)
        )
        conn.commit()

        return {
            "success": True,
            "type": row[2],
            "message": "Đã kích hoạt"
        }

    # Sai thiết bị
    if device and row[1] != device:
        return {
            "success": False,
            "message": "Key đã được sử dụng trên thiết bị khác"
        }

    return {
        "success": True,
        "type": row[2],
        "message": "Hợp lệ"
    }
    
@app.route("/new")
def new_key():
    key_type = request.args.get("type", "FREE").upper()
    days = int(request.args.get("days", "1"))

    key = create_key()
    expire = get_expire_time(days)

    page = create_key_page(key, key_type, expire)

    cursor.execute(
        """
        INSERT INTO keys
        (key, device_id, key_type, expire_time, telegraph_url)
        VALUES (?, ?, ?, ?, ?)
        """,
        (key, "", key_type, expire, page)
    )

    conn.commit()

    return {
        "success": True,
        "key": key,
        "type": key_type,
        "expire": expire,
        "page": page
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

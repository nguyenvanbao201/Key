from flask import Flask, jsonify, request

from database import (
    create_table,
    save_key,
    get_key,
    use_key,
    device_exists
)

from key import generate_key, get_expire_time
from telegraph_api import create_key_page
from link4m import create_short_link

from datetime import datetime

app = Flask(__name__)

create_table()


@app.route("/")
def home():
    return "VB TOOL API Running"


@app.route("/get-key")
def get_key_api():

    key = generate_key()

    created_at, expire_at = get_expire_time()

    telegraph_url = create_key_page(key)

    link4m_url = create_short_link(telegraph_url)

    save_key(
        key,
        telegraph_url,
        link4m_url,
        created_at,
        expire_at
    )

    return jsonify({
        "status": True,
        "link": link4m_url
    })


@app.route("/verify-key", methods=["POST"])
def verify():

    data = request.json

    key = data["key"]

    device = data["device"]

    row = get_key(key)

    if row is None:
        return jsonify({
            "status": False,
            "message": "Key không hợp lệ"
        })

    if row[7] == 1:
        return jsonify({
            "status": False,
            "message": "Key đã được sử dụng"
        })

    if device_exists(device):
        return jsonify({
            "status": False,
            "message": "Thiết bị đã kích hoạt"
        })

    expire = datetime.strptime(
        row[6],
        "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() > expire:
        return jsonify({
            "status": False,
            "message": "Key đã hết hạn"
        })

    use_key(key, device)

    return jsonify({
        "status": True,
        "message": "Xác thực thành công"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
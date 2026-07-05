from flask import Flask, redirect
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

    telegraph = create_telegraph_page(key)

    if telegraph:
        return redirect(telegraph)

    return "Không tạo được Telegraph"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
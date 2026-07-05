from flask import Flask
import random
import string

app = Flask(__name__)

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
    return f"Key mới: {key}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

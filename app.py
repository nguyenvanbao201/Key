from flask import Flask

app = Flask(name)

@app.route("/")
def home():
    return "VB Key API Running"

if name == "main":
    app.run(host="0.0.0.0", port=5000)

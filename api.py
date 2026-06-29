from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

@app.post("/check")
def check():
    data = request.json

    key = data["key"]
    hwid = data["hwid"]

    with open("license.json", "r", encoding="utf-8") as f:
        db = json.load(f)

    if key not in db:
        return jsonify({"success": False})

    info = db[key]

    if info["status"] != "active":
        return jsonify({"success": False})

    if datetime.now() > datetime.strptime(info["expire"], "%d/%m/%Y %H:%M:%S"):
        return jsonify({"success": False})

    if info["hwid"] == "":
        info["hwid"] = hwid

        with open("license.json", "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)

    elif info["hwid"] != hwid:
        return jsonify({"success": False})

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
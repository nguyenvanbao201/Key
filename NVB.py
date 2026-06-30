from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

@app.post("/check")
def check():
    data = request.json
    key = data["key"]

    with open("license.json", "r", encoding="utf-8") as f:
        db = json.load(f)

    if key not in db:
        return jsonify({"success": False})

    info = db[key]

    if info["status"] != "active":
        return jsonify({"success": False})

    expire = datetime.strptime(info["expire"], "%d/%m/%Y %H:%M:%S")

    if datetime.now() > expire:
        # Hết hạn -> xóa key
        del db[key]

        with open("license.json", "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4, ensure_ascii=False)

        return jsonify({"success": False})

    return jsonify({
        "success": True,
        "tool": info["tool"],
        "expire": info["expire"]
    })

if name == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

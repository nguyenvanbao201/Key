from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.post("/check")

def check():

    data = request.json

    key = data["key"]

    hwid = data["hwid"]

    with open("license.json","r") as f:
        db = json.load(f)

    if key not in db:
        return jsonify({"success":False})

    info = db[key]

    if info["status"] != "active":
        return jsonify({"success":False})

    if datetime.now() > datetime.strptime(info["expire"],"%Y-%m-%d %H:%M:%S"):
        return jsonify({"success":False})

    if info["hwid"] == "":
        info["hwid"] = hwid

        with open("license.json","w") as f:
            json.dump(db,f,indent=4)

    elif info["hwid"] != hwid:
        return jsonify({"success":False})

    return jsonify({"success":True})

import os

app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 10000))
)
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)   # <-- THIS enables browser permission (important)

FILE = "teachers.xlsx"

@app.route("/")
def home():
    return "KV Teacher Data Server Running"


@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.json

        # if no data received
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # append or create excel
        if os.path.exists(FILE):
            df = pd.read_excel(FILE)
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        else:
            df = pd.DataFrame([data])

        df.to_excel(FILE, index=False)

        return jsonify({"status": "saved"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run()

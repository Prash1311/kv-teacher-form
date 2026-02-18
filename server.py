from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
FILE = "teachers.xlsx"

@app.route("/")
def home():
    return "KV Teacher Data Server Running"

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    if os.path.exists(FILE):
        df = pd.read_excel(FILE)
        df = df._append(data, ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(FILE, index=False)

    return jsonify({"status":"saved"})

if __name__ == "__main__":
    app.run()

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
<<<<<<< HEAD
print("SERVER VERSION 3 LOADED")
=======
print("NEW VERSION RUNNING")
>>>>>>> 4f6475392fe3b0e00ae299a081eda23d9ea23ad0

app = Flask(__name__)
CORS(app)
print("NEW VERSION RUNNING")

FILE = "teachers.xlsx"


# -------------------------------
# Home route (health check)
# -------------------------------
@app.route("/")
def home():
    return "KV Teacher Data Server Running"


# -------------------------------
# Form submission route
# -------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.json

        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # Create or append Excel
        if os.path.exists(FILE):
            df = pd.read_excel(FILE)
            new_row = pd.DataFrame([data])
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            df = pd.DataFrame([data])

        df.to_excel(FILE, index=False)

        return jsonify({"status": "saved"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -------------------------------
# Download Excel route
# -------------------------------
@app.route("/download")
def download():
    if os.path.exists(FILE):
        return send_file(FILE, as_attachment=True)
    return "No data available yet. Submit a form first."
# -------------------------------
# Send data to dashboard
# -------------------------------
@app.route("/data")
def get_data():
    if not os.path.exists(FILE):
        return jsonify([])

    df = pd.read_excel(FILE)
    return df.fillna("").to_dict(orient="records")



# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
    app.run()

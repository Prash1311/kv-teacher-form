from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials

print("SERVER GOOGLE SHEET VERSION RUNNING")

app = Flask(__name__)
CORS(app)

# -------------------------------
# Google Sheet connection
# -------------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

sheet = client.open("KV_Teacher_Data").sheet1


# -------------------------------
# Health check route (Render needs this)
# -------------------------------
@app.route("/")
def home():
    return "KV Teacher Google Sheet Server Running"


# -------------------------------
# Form submission route
# -------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.json

        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # Map form data to sheet columns
        row = [
            data.get("Name",""),
            data.get("Email",""),
            data.get("Mobile",""),
            data.get("Date of Birth",""),
            data.get("Post Applied For",""),
            data.get("Subject",""),
            data.get("Address",""),
            data.get("Registration No","")
        ]

        sheet.append_row(row)

        return jsonify({"status": "saved"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -------------------------------
# Run server (Render compatible)
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

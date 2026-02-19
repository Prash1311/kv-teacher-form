from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

print("KV GOOGLE SHEET SERVER STARTING")

app = Flask(__name__)
CORS(app)

# -----------------------------------
# Google Sheet Setup
# -----------------------------------
SHEET_NAME = "KV_Teacher_Data"
CREDS_FILE = "creds.json"

def connect_sheet():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1

        print("Connected to Google Sheet:", SHEET_NAME)
        return sheet

    except Exception as e:
        print("SHEET CONNECTION ERROR:", str(e))
        return None

sheet = connect_sheet()


# -----------------------------------
# Health check (Render needs this)
# -----------------------------------
@app.route("/")
def home():
    return "KV Teacher Google Sheet Server Running"


# -----------------------------------
# Submit form
# -----------------------------------
@app.route("/submit", methods=["POST"])
def submit():
    global sheet

    try:
        if sheet is None:
            sheet = connect_sheet()
            if sheet is None:
                return jsonify({
                    "status":"error",
                    "message":"Cannot connect to Google Sheet (check creds or sharing)"
                }),500

        data = request.get_json(force=True)
        print("DATA RECEIVED:", data)

        # Required fields mapping
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

        print("WRITING ROW:", row)

        sheet.append_row(row, value_input_option="USER_ENTERED")

        print("WRITE SUCCESS")

        return jsonify({
            "status":"saved",
            "message":"Row added to sheet"
        })

    except Exception as e:
        print("WRITE FAILED:", str(e))
        return jsonify({
            "status":"error",
            "message":str(e)
        }),500


# -----------------------------------
# Run server (Render compatible)
# -----------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import base64
import io
from datetime import datetime

print("KV TEACHER FORM SERVER STARTING")

app = Flask(__name__)
CORS(app)

SHEET_NAME = "KV_Teacher_Data"

COLUMNS = [
    "Timestamp", "RegistrationNo", "Name", "FatherName", "Gender", "Category",
    "DateOfBirth", "Age", "Mobile", "Email", "Aadhar", "PAN", "Address",
    "PostApplied", "Subject",
    "XII_Year", "XII_Pct", "XII_Board",
    "Grad_Name", "Grad_Year", "Grad_Pct", "Grad_University",
    "PG_Name", "PG_Year", "PG_Pct", "PG_University",
    "BEd_Name", "BEd_Year", "BEd_Pct",
    "CTET", "CTETScore", "TotalExp", "Languages", "OtherInfo",
    "DeclPlace", "DeclDate", "Qualifications", "Experience",
]


def connect_sheet():
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = None

        # Option 1: Base64-encoded env var (most reliable — no newline corruption)
        b64 = os.environ.get("GOOGLE_CREDS_B64")
        if b64:
            creds_dict = json.loads(base64.b64decode(b64).decode("utf-8"))
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            print("✅ Creds loaded from GOOGLE_CREDS_B64")

        # Option 2: Raw JSON env var
        elif os.environ.get("GOOGLE_CREDS_JSON"):
            creds_dict = json.loads(os.environ.get("GOOGLE_CREDS_JSON"))
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            print("✅ Creds loaded from GOOGLE_CREDS_JSON")

        # Option 3: Render Secret File
        elif os.path.exists("/etc/secrets/creds.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/creds.json", scope)
            print("✅ Creds loaded from /etc/secrets/creds.json")

        # Option 4: Local dev
        elif os.path.exists("creds.json"):
            creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
            print("✅ Creds loaded from local creds.json")

        else:
            print("❌ No credentials found.")
            return None

        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1
        print("✅ Connected to Google Sheet:", SHEET_NAME)

        # Write header if sheet is empty
        if not sheet.row_values(1):
            sheet.insert_row(COLUMNS, index=1)
            print("📝 Header row created.")

        return sheet

    except Exception as e:
        print("❌ SHEET CONNECTION ERROR:", str(e))
        return None


sheet = connect_sheet()


@app.route("/")
def home():
    return "KV Teacher Form Server Running ✅"


@app.route("/submit", methods=["POST"])
def submit():
    global sheet
    try:
        if sheet is None:
            sheet = connect_sheet()
        if sheet is None:
            return jsonify({"status": "error", "message": "Cannot connect to Google Sheet"}), 500

        data = request.get_json(force=True)
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # Validate required fields
        for field in ["Name", "Mobile", "Email"]:
            if not data.get(field, "").strip():
                return jsonify({"status": "error", "message": f"{field} is required"}), 400

        reg_no = "KV-KRP-" + datetime.now().strftime("%Y%m%d%H%M%S")
        timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        row = []
        for col in COLUMNS:
            if col == "Timestamp":
                row.append(timestamp)
            elif col == "RegistrationNo":
                row.append(reg_no)
            else:
                row.append(data.get(col, ""))

        sheet.append_row(row, value_input_option="USER_ENTERED")
        print(f"✅ Saved: {reg_no} | {data.get('Name')} | {data.get('PostApplied')}")

        return jsonify({"status": "saved", "registration": reg_no})

    except Exception as e:
        print("❌ SUBMIT ERROR:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/data", methods=["GET"])
def get_data():
    global sheet
    try:
        if sheet is None:
            sheet = connect_sheet()
        if sheet is None:
            return jsonify([])
        records = sheet.get_all_records()
        return jsonify(records)
    except Exception as e:
        print("❌ DATA ERROR:", str(e))
        return jsonify([]), 500


@app.route("/download", methods=["GET"])
def download():
    global sheet
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment

        if sheet is None:
            sheet = connect_sheet()

        records = sheet.get_all_records()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Applications"

        if records:
            ws.append(list(records[0].keys()))
            for rec in records:
                ws.append(list(rec.values()))

            # Style header row
            for cell in ws[1]:
                cell.font      = Font(bold=True, color="FFFFFF")
                cell.fill      = PatternFill("solid", fgColor="0D47A1")
                cell.alignment = Alignment(horizontal="center")

            # Auto column width
            for col in ws.columns:
                width = max(len(str(c.value or "")) for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(width + 4, 50)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        filename = f"KV_Applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(
            buf,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename
        )

    except ImportError:
        return jsonify({"status": "error", "message": "Add openpyxl to requirements.txt"}), 500
    except Exception as e:
        print("❌ DOWNLOAD ERROR:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
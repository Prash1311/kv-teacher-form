from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
import base64
import pandas as pd

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# The CSV export link for your Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1nh4-S5SjXpRNrZKPBxfx4x1adEDjxFqjcIIDNBO_JhA/export?format=csv"
UPLOAD_FOLDER = "applications"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "KV K.R. Puram API Server is Live"

# --- 1. DATA ROUTE (Fixes "Applicant 1" issue) ---
@app.route("/data")
def get_data():
    """Fetches real-time data from Google Sheets for the dashboard."""
    try:
        # Pulls live data including names: RENUKA, SONI KUMARI, etc.
        df = pd.read_csv(SHEET_URL)
        # Replacing NaN with empty strings to avoid JSON errors
        data = df.fillna("").to_dict(orient="records")
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 2. DOWNLOAD ROUTE (Fixes Excel download) ---
@app.route("/download")
def download_excel():
    """Generates and serves an Excel file from the Google Sheet data."""
    try:
        df = pd.read_csv(SHEET_URL)
        
        # Use BytesIO to create the file in memory (important for Render)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Applicants')
        
        output.seek(0)
        
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="KV_Teacher_Applications.xlsx"
        )
    except Exception as e:
        return f"Error generating Excel: {str(e)}", 500

# --- 3. PDF GENERATION ROUTE ---
@app.route("/save-pdf", methods=["POST"])
def save_pdf():
    """Generates a PDF for a specific candidate and saves it to the server."""
    try:
        data = request.json
        # Extracting real name and registration
        name = data.get("Name", "Candidate").replace(" ", "_")
        reg = data.get("RegistrationNo", "TEMP")

        filename = f"{UPLOAD_FOLDER}/{reg}_{name}.pdf"
        c = canvas.Canvas(filename, pagesize=A4)

        # Basic layout
        y = 800
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Application: {reg}")
        y -= 30
        
        c.setFont("Helvetica", 10)
        # Iterating through data fields
        for key, value in data.items():
            if key in ["Photo", "Qualifications", "Experience"]:
                continue
            if y < 50: # Simple page break check
                c.showPage()
                y = 800
            
            c.drawString(50, y, f"{key}: {str(value)[:90]}")
            y -= 18

        # Handling Photo
        photo_base64 = data.get("Photo")
        if photo_base64 and "," in photo_base64:
            try:
                header, encoded = photo_base64.split(",", 1)
                img_bytes = base64.b64decode(encoded)
                img = ImageReader(BytesIO(img_bytes))
                # Placing photo in top right
                c.drawImage(img, 430, 650, width=120, height=150)
            except:
                pass # Skip photo if decoding fails

        c.save()
        return jsonify({"status": "saved", "file": filename})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Port 5000 for local, Render will provide its own port via environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

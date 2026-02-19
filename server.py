from flask import Flask, request, jsonify
from flask_cors import CORS
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os, base64
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Folder to store PDFs
UPLOAD_FOLDER = "applications"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "KV Application PDF Server Running"


@app.route("/save-pdf", methods=["POST"])
def save_pdf():
    try:
        data = request.json

        name = data.get("Name", "Candidate").replace(" ", "_")
        reg = data.get("registration", "TEMP")

        filename = f"{UPLOAD_FOLDER}/{reg}_{name}.pdf"

        c = canvas.Canvas(filename, pagesize=A4)

        # ---------------- TEXT ----------------
        y = 800
        for key, value in data.items():
            if key == "Photo":
                continue
            c.drawString(50, y, f"{key}: {str(value)[:95]}")
            y -= 18

        # ---------------- PHOTO ----------------
        photo_data = data.get("Photo")

        if photo_data:
            header, encoded = photo_data.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            img = ImageReader(BytesIO(img_bytes))
            c.drawImage(img, 430, 650, width=120, height=150)

        c.save()

        return jsonify({"status": "saved", "file": filename})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

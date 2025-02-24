from flask import Flask, request, jsonify, render_template, Response, send_file
from flask_cors import CORS
import cv2
import numpy as np
import requests
import json
import sqlite3
import pandas as pd
from pyzbar.pyzbar import decode

app = Flask(__name__)
CORS(app)  # ✅ อนุญาตให้ Netlify เรียก API ได้

# ✅ ตั้งค่า Google Apps Script Webhook
GAS_WEBHOOK_URL = "https://script.google.com/macros/s/YOUR_GAS_SCRIPT/exec"

# ✅ ฟังก์ชันส่งข้อมูลไป Google Sheets
def send_to_google_sheets(barcode_text):
    data = {"barcode": barcode_text}
    headers = {"Content-Type": "application/json"}
    response = requests.post(GAS_WEBHOOK_URL, headers=headers, data=json.dumps(data))
    return response.text

# ✅ ฟังก์ชันบันทึกบาร์โค้ดลงฐานข้อมูล SQLite
def save_to_db(barcode_text):
    conn = sqlite3.connect('scans.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            barcode TEXT, 
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("INSERT INTO scans (barcode) VALUES (?)", (barcode_text,))
    conn.commit()
    conn.close()

# ✅ API รับข้อมูลบาร์โค้ดจาก Netlify
@app.route('/scan', methods=['POST'])
def scan_barcode():
    data = request.get_json()
    barcode = data.get("barcode")
    if barcode:
        save_to_db(barcode)  # บันทึกลงฐานข้อมูล
        send_to_google_sheets(barcode)  # ส่งไป Google Sheets
        return jsonify({"message": "Barcode saved!", "barcode": barcode})
    return jsonify({"error": "No barcode received"}), 400

# ✅ API ให้ดาวน์โหลดข้อมูล CSV
@app.route('/export')
def export_data():
    conn = sqlite3.connect('scans.db')
    df = pd.read_sql_query("SELECT * FROM scans", conn)
    conn.close()

    file_path = "exported_scans.csv"
    df.to_csv(file_path, index=False)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

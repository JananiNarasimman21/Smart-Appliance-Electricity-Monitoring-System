from flask import Flask, render_template, send_file, request, jsonify
import pandas as pd
import os
import asyncio
from kasa import Discover, Credentials
from kasa.module import Module
import sqlite3
from datetime import datetime

# PDF imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

# -----------------------------
# Appliance mapping
# -----------------------------
appliance_map = {
    "Appliance1": "Geyser",
    "Appliance2": "Fridge",
    "Appliance3": "Microwave",
    "Appliance4": "AirConditioner",
    "Appliance5": "WashingMachine",
    "Appliance6": "Television",
    "Appliance7": "WaterPurifier",
    "Appliance8": "ElectricKettle",
    "Appliance9": "LaptopCharger"
}

# -----------------------------
# Tariff Function
# -----------------------------
def tariff(units):
    cost = 0

    if units <= 100:
        cost = 0
    elif units <= 200:
        cost = (units - 100) * 2.25
    elif units <= 400:
        cost = (100 * 2.25) + (units - 200) * 4.5
    elif units <= 500:
        cost = (100 * 2.25) + (200 * 4.5) + (units - 400) * 6
    elif units <= 600:
        cost = (100 * 2.25) + (200 * 4.5) + (100 * 6) + (units - 500) * 8
    elif units <= 800:
        cost = (100 * 2.25) + (200 * 4.5) + (100 * 6) + (100 * 8) + (units - 600) * 9
    elif units <= 1000:
        cost = (100 * 2.25) + (200 * 4.5) + (100 * 6) + (100 * 8) + (200 * 9) + (units - 800) * 10
    else:
        cost = (100 * 2.25) + (200 * 4.5) + (100 * 6) + (100 * 8) + (200 * 9) + (200 * 10) + (units - 1000) * 11

    return cost

# -----------------------------
# STORE DATA
# -----------------------------
def store_data(power, today_energy, month_energy, today_cost, month_cost):

    conn = sqlite3.connect("energy.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS realtime_energy(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        power REAL,
        today_energy REAL,
        month_energy REAL,
        today_cost REAL,
        month_cost REAL
    )
    """)

    cursor.execute("""
    INSERT INTO realtime_energy
    (timestamp, power, today_energy, month_energy, today_cost, month_cost)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(),
        power,
        today_energy,
        month_energy,
        today_cost,
        month_cost
    ))

    conn.commit()
    conn.close()

# -----------------------------
# GET ENERGY FROM TAPO
# -----------------------------
async def get_energy(ip, email, password):

    creds = Credentials(email, password)

    device = await Discover.discover_single(ip, credentials=creds)
    await device.update()

    energy_module = device.modules.get(Module.Energy)

    power = energy_module.current_consumption
    energy_today = energy_module.consumption_today or 0
    energy_month = energy_module.consumption_this_month or 0

    today_cost = tariff(energy_today)
    month_cost = tariff(energy_month)

    # store data
    store_data(power, energy_today, energy_month, today_cost, month_cost)

    return {
        "power": power,
        "energy": energy_today,
        "month_energy": energy_month,
        "cost": today_cost,
        "month_cost": month_cost
    }

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/instructions")
def instructions():
    return render_template("instructions.html")

@app.route("/appliance")
def appliance():
    return render_template("appliance.html")

@app.route("/datatype/<appliance>")
def datatype(appliance):
    return render_template("datatype.html", appliance=appliance)

@app.route("/data/<appliance>/<dtype>")
def data(appliance, dtype):

    name = appliance_map.get(appliance, appliance)
    file = f"output/{name}_{dtype}.csv"

    if not os.path.exists(file):
        return f"{file} not found."

    df = pd.read_csv(file)
    rows = df.to_dict(orient="records")

    return render_template("data.html", appliance=name, dtype=dtype, rows=rows)

@app.route("/download/<appliance>/<dtype>")
def download(appliance, dtype):

    name = appliance_map.get(appliance, appliance)
    file = f"output/{name}_{dtype}.csv"

    if not os.path.exists(file):
        return f"{file} not found."

    return send_file(file, as_attachment=True)

@app.route("/realtime")
def realtime():
    return render_template("realtime.html")

# -----------------------------
# 🔥 ACCURACY API (FINAL)
# -----------------------------
@app.route("/accuracy_api")
def accuracy_api():

    conn = sqlite3.connect("energy.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT today_energy FROM realtime_energy
    ORDER BY id DESC LIMIT 2
    """)

    rows = cursor.fetchall()
    conn.close()

    if len(rows) < 2:
        return jsonify({
            "accuracy": 0,
            "tapo": 0,
            "dashboard": 0
        })

    tapo_energy = rows[0][0]
    dashboard_energy = rows[1][0]

    if dashboard_energy > 0:
        accuracy = (tapo_energy / dashboard_energy) * 100
    else:
        accuracy = 0

    return jsonify({
        "tapo": round(tapo_energy, 4),
        "dashboard": round(dashboard_energy, 4),
        "accuracy": round(accuracy, 2)
    })

# -----------------------------
# LIVE DATA API
# -----------------------------
@app.route("/livepower", methods=["POST"])
def livepower():

    data = request.get_json()

    ip = data.get("ip")
    email = data.get("email")
    password = data.get("password")

    try:
        result = asyncio.run(get_energy(ip, email, password))
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

# -----------------------------
# DOWNLOAD PDF
# -----------------------------
@app.route("/download_pdf", methods=["POST"])
def download_pdf():

    power = request.form.get("power")
    energy = request.form.get("energy")
    cost = request.form.get("cost")
    month_cost = request.form.get("month_cost")

    file_path = "Electricity_Bill.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Electricity Bill Report", styles['Title']))
    content.append(Spacer(1, 20))

    content.append(Paragraph(f"Current Power: {power} W", styles['Normal']))
    content.append(Paragraph(f"Today's Energy: {energy} kWh", styles['Normal']))
    content.append(Paragraph(f"Today's Cost: ₹{cost}", styles['Normal']))
    content.append(Paragraph(f"Monthly Cost: ₹{month_cost}", styles['Normal']))

    doc.build(content)

    return send_file(file_path, as_attachment=True)

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
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
    "Appliance2": "Refrigerator",
    "Appliance3": "Microwave",
    "Appliance4": "InductionCooktop",
    "Appliance5": "WashingMachine",
    "Appliance6": "Television",
    "Appliance7": "WaterPurifier",
    "Appliance8": "ElectricKettle",
    "Appliance9": "LaptopCharger",
    "Appliance10": "TableFan",
    "Appliance11": "IronBox",
    "Appliance12": "RiceCooker",
    "Appliance13": "MixerGrinder",
    "Appliance14": "Toaster",
    "Appliance15": "CoffeeMaker",
    "Appliance16": "DesktopPC",
    "Appliance17": "WiFiRouter",
    "Appliance18": "PhoneCharger",
    "Appliance19": "AirPurifier",
    "Appliance20": "VacuumCleaner",
    "Appliance21": "WaterMotor"
}

appliance_images = {
    "Geyser": "mode_heat",
    "Refrigerator": "kitchen",
    "Microwave": "microwave",
    "InductionCooktop": "soup_kitchen",
    "WashingMachine": "local_laundry_service",
    "Television": "tv",
    "WaterPurifier": "water_drop",
    "ElectricKettle": "emoji_food_beverage",
    "LaptopCharger": "laptop_chromebook",
    "TableFan": "mode_fan",
    "IronBox": "iron",
    "RiceCooker": "rice_bowl",
    "MixerGrinder": "blender",
    "Toaster": "toaster",
    "CoffeeMaker": "coffee_maker",
    "DesktopPC": "desktop_windows",
    "WiFiRouter": "router",
    "PhoneCharger": "smartphone",
    "AirPurifier": "air",
    "VacuumCleaner": "vacuum",
    "WaterMotor": "water"
}

supported_data_types = ("daily", "monthly")


def ensure_realtime_schema(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS realtime_energy(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        appliance TEXT,
        power REAL,
        today_energy REAL,
        month_energy REAL,
        today_cost REAL,
        month_cost REAL
    )
    """)

    cursor.execute("PRAGMA table_info(realtime_energy)")
    columns = [row[1] for row in cursor.fetchall()]
    if "appliance" not in columns:
        cursor.execute("ALTER TABLE realtime_energy ADD COLUMN appliance TEXT DEFAULT 'Unknown'")


def get_appliance_items():
    items = []
    for appliance_id, name in appliance_map.items():
        items.append({
            "id": appliance_id,
            "name": name,
            "icon": appliance_images.get(name, "electrical_services"),
            "data_types": list(supported_data_types)
        })
    return items


def resolve_output_file(appliance, dtype):
    if dtype not in supported_data_types:
        return None, None

    name = appliance_map.get(appliance, appliance)
    file_path = os.path.join("output", f"{name}_{dtype}.csv")
    return name, file_path


def load_output_rows(appliance, dtype):
    name, file_path = resolve_output_file(appliance, dtype)
    if not file_path or not os.path.exists(file_path):
        return name, None

    df = pd.read_csv(file_path)
    return name, df.to_dict(orient="records")


def fetch_latest_realtime_row(appliance=None):
    conn = sqlite3.connect("energy.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        ensure_realtime_schema(cursor)
        if appliance:
            cursor.execute("""
            SELECT timestamp, appliance, power, today_energy, month_energy, today_cost, month_cost
            FROM realtime_energy
            WHERE appliance = ?
            ORDER BY id DESC LIMIT 1
            """, (appliance,))
        else:
            cursor.execute("""
            SELECT timestamp, appliance, power, today_energy, month_energy, today_cost, month_cost
            FROM realtime_energy
            ORDER BY id DESC LIMIT 1
            """)
    except sqlite3.OperationalError:
        conn.close()
        return None

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "timestamp": row["timestamp"],
        "appliance": row["appliance"],
        "power": row["power"],
        "today_energy": row["today_energy"],
        "month_energy": row["month_energy"],
        "today_cost": row["today_cost"],
        "month_cost": row["month_cost"]
    }


def fetch_top_power_appliance():
    conn = sqlite3.connect("energy.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        ensure_realtime_schema(cursor)
        cursor.execute("""
        SELECT appliance, AVG(power) AS avg_power, MAX(power) AS peak_power
        FROM realtime_energy
        WHERE power IS NOT NULL
        GROUP BY appliance
        ORDER BY avg_power DESC
        LIMIT 1
        """)
        row = cursor.fetchone()
    except sqlite3.OperationalError:
        conn.close()
        return None

    conn.close()
    if not row:
        return None

    appliance_id = row["appliance"]
    return {
        "id": appliance_id,
        "name": appliance_map.get(appliance_id, appliance_id),
        "avg_power": round(float(row["avg_power"] or 0), 2),
        "peak_power": round(float(row["peak_power"] or 0), 2)
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
def store_data(appliance, power, today_energy, month_energy, today_cost, month_cost):

    conn = sqlite3.connect("energy.db")
    cursor = conn.cursor()

    ensure_realtime_schema(cursor)

    cursor.execute("""
    INSERT INTO realtime_energy
    (timestamp, appliance, power, today_energy, month_energy, today_cost, month_cost)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now(),
        appliance,
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
async def get_energy(appliance, ip, email, password):
    creds = Credentials((email or "").strip(), password or "")
    device = await Discover.discover_single((ip or "").strip(), credentials=creds)
    await device.update()

    energy = device.modules.get(Module.Energy)
    if energy is None:
        raise RuntimeError("Energy module not available on this device.")

    power = float(energy.current_consumption or 0)
    energy_today = float(energy.consumption_today or 0)
    energy_month = float(energy.consumption_this_month or 0)

    today_cost = tariff(energy_today)
    month_cost = tariff(energy_month)

    # store data
    store_data(appliance, power, energy_today, energy_month, today_cost, month_cost)

    return {
        "appliance": appliance_map.get(appliance, appliance),
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
    name, rows = load_output_rows(appliance, dtype)
    if rows is None:
        return f"output/{name}_{dtype}.csv not found."

    return render_template("data.html", appliance=name, dtype=dtype, rows=rows)

@app.route("/download/<appliance>/<dtype>")
def download(appliance, dtype):
    name, file_path = resolve_output_file(appliance, dtype)
    if not file_path or not os.path.exists(file_path):
        return f"output/{name}_{dtype}.csv not found."

    return send_file(file_path, as_attachment=True)

@app.route("/realtime")
def realtime():
    appliance = request.args.get("appliance", "").strip()
    appliance_name = appliance_map.get(appliance, "")
    return render_template("realtime.html", appliance=appliance, appliance_name=appliance_name)


@app.route("/history")
def history():
    appliance = request.args.get("appliance", "").strip()
    appliance_name = appliance_map.get(appliance, "")
    return render_template("history.html", appliance=appliance, appliance_name=appliance_name)


@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok"})


@app.route("/api/appliances")
def api_appliances():
    return jsonify({"appliances": get_appliance_items()})


@app.route("/api/data/<appliance>/<dtype>")
def api_data(appliance, dtype):
    name, rows = load_output_rows(appliance, dtype)
    if rows is None:
        return jsonify({"error": f"No {dtype} data found for {name}."}), 404

    return jsonify({
        "appliance": {
            "id": appliance,
            "name": name
        },
        "dtype": dtype,
        "rows": rows
    })


@app.route("/api/realtime/latest")
def api_realtime_latest():
    appliance = request.args.get("appliance", "").strip() or None
    latest = fetch_latest_realtime_row(appliance=appliance)
    if latest is None:
        return jsonify({
            "timestamp": None,
            "appliance": appliance_map.get(appliance, appliance) if appliance else None,
            "power": 0,
            "today_energy": 0,
            "month_energy": 0,
            "today_cost": 0,
            "month_cost": 0
        })

    return jsonify(latest)


@app.route("/api/power/top")
def api_power_top():
    top = fetch_top_power_appliance()
    if top is None:
        return jsonify({
            "id": None,
            "name": None,
            "avg_power": 0,
            "peak_power": 0
        })
    return jsonify(top)


@app.route("/api/history")
def api_history():
    appliance = request.args.get("appliance", "").strip()
    period = request.args.get("period", "daily").strip().lower()
    if period not in {"daily", "monthly"}:
        return jsonify({"error": "period must be daily or monthly"}), 400
    if not appliance:
        return jsonify({"error": "appliance is required"}), 400

    conn = sqlite3.connect("energy.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    ensure_realtime_schema(cursor)

    if period == "daily":
        cursor.execute("""
        SELECT date(timestamp) as label,
               AVG(today_energy) as energy,
               AVG(today_cost) as cost
        FROM realtime_energy
        WHERE appliance = ?
        GROUP BY date(timestamp)
        ORDER BY date(timestamp) DESC
        LIMIT 30
        """, (appliance,))
    else:
        cursor.execute("""
        SELECT strftime('%Y-%m', timestamp) as label,
               AVG(month_energy) as energy,
               AVG(month_cost) as cost
        FROM realtime_energy
        WHERE appliance = ?
        GROUP BY strftime('%Y-%m', timestamp)
        ORDER BY strftime('%Y-%m', timestamp) DESC
        LIMIT 12
        """, (appliance,))

    rows = cursor.fetchall()
    conn.close()
    history_rows = [{
        "label": row["label"],
        "energy": round(float(row["energy"] or 0), 4),
        "cost": round(float(row["cost"] or 0), 2)
    } for row in rows]

    return jsonify({
        "appliance": {
            "id": appliance,
            "name": appliance_map.get(appliance, appliance)
        },
        "period": period,
        "rows": history_rows
    })

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

    data = request.get_json(silent=True) or {}

    appliance = (data.get("appliance") or "").strip()
    ip = (data.get("ip") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not appliance or appliance not in appliance_map:
        return jsonify({"error": "valid appliance is required"}), 400
    if not ip or not email or not password:
        return jsonify({"error": "ip, email, and password are required"}), 400

    try:
        result = asyncio.run(get_energy(appliance, ip, email, password))
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    # Default to HTTP for local mobile testing; set FLASK_HTTPS=1 when needed.
    use_https_raw = os.environ.get("FLASK_HTTPS", "0").strip().lower()
    use_https = use_https_raw not in {"0", "false", "no", "off"}

    cert_file = os.environ.get("SSL_CERT_FILE", "").strip()
    key_file = os.environ.get("SSL_KEY_FILE", "").strip()

    ssl_context = None
    if use_https:
        if cert_file and key_file and os.path.exists(cert_file) and os.path.exists(key_file):
            ssl_context = (cert_file, key_file)
        else:
            ssl_context = "adhoc"

    protocol = "https" if use_https else "http"
    print(f"Starting server on {protocol}://0.0.0.0:5000")
    print(f"LAN URL: {protocol}://<your-pc-ip>:5000")
    if use_https and ssl_context == "adhoc":
        print("Using temporary self-signed certificate (browser warning is expected).")
        print("Set SSL_CERT_FILE and SSL_KEY_FILE to use a trusted local certificate.")

    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context=ssl_context)

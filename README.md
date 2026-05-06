# Tariff Aware Appliance Level Electricity Monitoring and Billing

## Project Overview
The **Tariff Aware Appliance Level Electricity Monitoring and Billing System** is a real-time web application that monitors electricity usage of individual appliances and calculates cost based on Tamil Nadu electricity tariff rules.

This project focuses on **live IoT smart plug readings, tariff-based billing, real-time dashboards, and SQLite-based history tracking**.

## Features

- Real-time power monitoring using Tapo smart plug
- Appliance-level energy consumption tracking
- Daily and monthly electricity cost calculation
- Tariff-aware billing system
- Historical usage and cost tracking from stored live readings
- CSV and PDF report download
- SQLite database storage
- Simple web and Android-friendly interface

## Technologies Used

- Python (Flask)
- HTML, CSS
- SQLite Database
- python-kasa (IoT integration)
- ReportLab
- Android app using Kotlin and Jetpack Compose

## Project Structure

`eb_bill_project/`

- `app.py`
- `realtime_energy.py`
- `tariff.py`
- `energy.db`
- `templates/`
- `static/`
- `android_app/`
- `diagrams/`
- `README.md`

## How It Works

1. Tapo smart plug measures real-time power consumption.
2. Flask backend retrieves the live device readings using `python-kasa`.
3. Daily and monthly energy values are processed.
4. Tamil Nadu tariff rules are applied to calculate cost.
5. Data is stored in SQLite database.
6. Results are displayed on the dashboard and history screens.
7. Reports can be downloaded as CSV or PDF.

## Tariff Calculation (Tamil Nadu EB)

| Units | Rate |
|------|------|
| 0-100 | Free |
| 101-200 | Rs 2.25/unit |
| 201-400 | Rs 4.5/unit |
| 401-500 | Rs 6/unit |
| 501-600 | Rs 8/unit |
| 601-800 | Rs 9/unit |
| 801-1000 | Rs 10/unit |
| >1000 | Rs 11/unit |

## How to Run

### 1. Install dependencies
```bash
pip install flask python-kasa reportlab
```

### 2. Start the Flask backend
```bash
python app.py
```

The backend exposes these main JSON endpoints:

- `/api/health`
- `/api/appliances`
- `/api/realtime/latest`
- `/api/power/top`
- `/api/energy/top`
- `/api/energy/ranking`
- `/api/history`
- `/livepower`
- `/accuracy_api`

## Android App

A native Android project is available in [android_app](./android_app).

### What it includes

- Kotlin + Jetpack Compose UI
- Appliance list and report viewer
- Real-time monitoring screen for Tapo smart plug data
- Configurable Flask server URL for LAN access from mobile devices

### How to run the Android app

1. Open the `android_app` folder in Android Studio.
2. Let Gradle sync and install any requested SDK components.
3. Start the Flask backend with `python app.py`.
4. Connect your Android phone or emulator to the same network as your PC.
5. Set the backend URL in the app, for example `http://192.168.1.10:5000`.
6. Run the app on your emulator or Android phone.

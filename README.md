# ⚡ Tariff Aware Appliance Level Electricity Cost Prediction

## 📌 Project Overview
The **Tariff Aware Appliance Level Electricity Cost Prediction System** is a real-time web application that monitors electricity usage of individual appliances and calculates the cost based on Tamil Nadu electricity tariff rules.

This project integrates **IoT smart plug data, dataset analysis, and tariff-based billing** to provide accurate and intelligent electricity monitoring.

---

## 🚀 Features

✅ Real-time power monitoring using smart plug  
✅ Appliance-level energy consumption tracking  
✅ Daily and monthly electricity cost calculation  
✅ Tariff-aware billing system  
✅ Historical data analysis using REFIT dataset  
✅ CSV report download  
✅ SQLite database storage  
✅ Simple and user-friendly interface  

---

## 🛠️ Technologies Used

- Python (Flask)
- HTML, CSS
- SQLite Database
- Pandas
- python-kasa (IoT integration)
- REFIT Dataset

---

## ⚙️ Project Structure
eb_bill_project/ │ ├── app.py ├── dataset_cost.py ├── realtime_energy.py ├── tariff.py ├── energy.db │ ├── templates/ │   ├── welcome.html │   ├── instructions.html │   ├── appliance.html │   ├── datatype.html │   ├── data.html │   ├── realtime.html │ ├── static/ ├── dataset/ ├── output/ └── README.md
---

## 📊 How It Works

1. Smart plug measures real-time power consumption  
2. Flask backend retrieves energy data  
3. Energy is converted into kWh  
4. Tamil Nadu tariff rules are applied  
5. Cost is calculated automatically  
6. Data is stored in SQLite database  
7. Results displayed on web dashboard  

---

## 💡 Tariff Calculation (Tamil Nadu EB)

| Units | Rate |
|------|------|
| 0–100 | Free |
| 101–200 | ₹2.25/unit |
| 201–400 | ₹4.5/unit |
| 401–500 | ₹6/unit |
| 501–600 | ₹8/unit |
| 601–800 | ₹9/unit |
| 801–1000 | ₹10/unit |
| >1000 | ₹11/unit |

---

## ▶️ How to Run    
python dataset_cost.py

python app.py

### 1️⃣ Install dependencies
```bash
pip install flask pandas python-kasa
```

### 2. Start the Flask backend
```bash
python app.py
```

The backend now exposes Android-friendly JSON endpoints:

- `/api/health`
- `/api/appliances`
- `/api/data/<appliance>/<dtype>`
- `/api/realtime/latest`
- `/livepower`
- `/accuracy_api`

## Android App

A native Android project has been added in [android_app](./android_app).

### What it includes

- Kotlin + Jetpack Compose UI
- Appliance list and report viewer
- Real-time monitoring screen for Tapo smart plug data
- Configurable Flask server URL so your phone can connect to your PC over Wi-Fi

### How to run the Android app

1. Install Android Studio on your computer.
2. Open the `android_app` folder in Android Studio.
3. Let Gradle sync and install any requested SDK components.
4. Start your Flask backend with `python app.py`.
5. Make sure your Android phone or emulator and PC can reach each other.
6. In the app, set the backend URL to your computer's LAN address, for example `http://192.168.1.10:5000`.
7. Run the app on an emulator or Android phone.

### Important note

This environment did not have `java`, `adb`, or Android build tools installed, so the Android project files were created but the APK was not built here.

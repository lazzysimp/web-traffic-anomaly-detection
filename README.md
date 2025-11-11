# 🚀 Real-Time DDoS Detection & Traffic Monitoring System

A real-time web traffic monitoring and DDoS detection system using **Flask**, **Socket.IO**, **Bootstrap 5**, and **Chart.js**.
It tracks IPs, detects traffic spikes, identifies suspicious activity, performs country lookup, and displays all traffic on a live dashboard.
Includes a dummy site endpoint for testing.

---

## ✅ Features

* Real-time IP tracking
* Country lookup using geolocation API
* Automatic DDoS anomaly detection
* Live charts (bar & pie)
* Instant updates via Socket.IO
* Auto-block malicious IPs
* Dummy testing website
* Traffic logs + alerts panel

---

## 📦 Installation

### 1️⃣ Clone the Repository

```
git clone https://github.com/yourusername/ddos-detection-system.git
cd ddos-detection-system
```

### 2️⃣ Create Virtual Environment

```
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

## ▶️ Run the Application

Start the server:

```
python app.py
```

You should see:

```
Running on http://127.0.0.1:5000
```

---

## 🌐 Access the Dashboard

Dashboard:

```
http://127.0.0.1:5000/dashboard
```

Dummy test page:

```
http://127.0.0.1:5000/dummy
```

---

## 📱 Access From Mobile (Same WiFi)

1. Find your computer’s local IP:

```
ip addr show
```

Example: `192.168.1.5`

2. Open on mobile:

```
http://192.168.1.5:5000/dummy
```

You will now see your phone's IP on the dashboard.

---

## 🧪 Generate Test Traffic

Use:

* The “Generate Test Traffic” button on the dashboard
* Or manually refresh the dummy page rapidly
* Or use a script/tool (e.g., Python load generator, curl, etc.)

---

## 📂 Folder Structure
│
├── app.py                 # Main Flask backend
├── requirements.txt       # Python dependencies
│
├── templates              # HTML templates folder
│   ├── index.html         # Dummy website
│   └── dashboard.html     # Real-time dashboard UI

---

## 🛠 Technologies Used

* Python (Flask Framework)
* Flask-SocketIO
* Bootstrap 5
* Chart.js
* Requests (IP → Country lookup)

---

## 🤝 Contributing

Pull requests are welcome!
Feel free to suggest improvements or report issues.

---
✅ a **preview GIF**,
✅ or a **project logo**.

from flask import Flask, render_template, request, abort, jsonify
from flask_socketio import SocketIO
from collections import defaultdict, deque
import time, requests, json, threading

import eventlet
eventlet.monkey_patch()

# -------------------
# Config
# -------------------
REQUEST_LIMIT = 20
TIME_WINDOW = 10
AUTO_BLOCK = True

# -------------------
# App setup
# -------------------
app = Flask(__name__)
app.template_folder = 'templates'
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

# In-memory data stores
request_log = defaultdict(lambda: deque(maxlen=1000))
anomalies = []
blocked_ips = set()
ip_country_cache = {}
lock = threading.Lock()


# -------------------
# SocketIO Event Handlers
# -------------------
@socketio.on('connect')
def handle_connect():
    """Send the current list of blocked IPs to a newly connected client."""
    print("Client connected, sending current blocklist.")
    socketio.emit('update_blocked_list', {'blocked_ips': list(blocked_ips)})


# -------------------
# Helpers
# -------------------
def fetch_country_requests(ip):
    if ip.startswith("127.") or ip.startswith("192.168.") or ip.startswith("10."): return "Local Network"
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=country", timeout=2)
        response.raise_for_status()
        return response.json().get("country", "Unknown")
    except requests.RequestException: return "Unknown"

def resolve_country_background(ip, count):
    if ip_country_cache.get(ip) != "Resolving...": return
    country = fetch_country_requests(ip)
    ip_country_cache[ip] = country
    socketio.emit("traffic_update", {"ip": ip, "count": count, "country": country, "last_seen": time.strftime("%H:%M:%S")})

def log_anomaly_background(anomaly):
    try:
        with open("anomalies.log", "a") as f: f.write(f"{json.dumps(anomaly)}\n")
    except Exception as e: print(f"Error writing to anomaly log: {e}")


# -------------------
# Middleware: Monitor requests
# -------------------
@app.before_request
def monitor_requests():
    path = request.path or ""
    if path.startswith("/dashboard") or path.startswith("/unblock") or path.startswith("/static") or path == "/favicon.ico": return

    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    if ip in blocked_ips: abort(403)

    now = time.time()
    with lock:
        request_log[ip].append(now)
        recent = [t for t in request_log[ip] if t >= now - TIME_WINDOW]
        request_log[ip] = deque(recent, maxlen=1000)
        count = len(recent)

    # --- THIS IS THE CORRECTED LOGIC ---
    country = ip_country_cache.get(ip)  # Check cache without a default value
    if country is None:
        # If the IP is new, set the cache to "Resolving..." and start the background task
        ip_country_cache[ip] = "Resolving..."
        country = "Resolving..."
        socketio.start_background_task(resolve_country_background, ip, count)
    
    socketio.emit("traffic_update", {"ip": ip, "count": count, "country": country, "last_seen": time.strftime("%H:%M:%S")})

    if count > REQUEST_LIMIT:
        resolved_country = ip_country_cache.get(ip, "Unknown")
        anomaly = {"ip": ip, "count": count, "country": resolved_country, "timestamp": int(now)}
        with lock:
            last = anomalies[-1] if anomalies else None
            if not last or last.get("ip") != ip:
                anomalies.append(anomaly)
                socketio.start_background_task(log_anomaly_background, anomaly)
                socketio.emit("ddos_alert", anomaly)
                if AUTO_BLOCK and ip not in blocked_ips:
                    blocked_ips.add(ip)
                    print(f"[AUTO-BLOCK] {ip} ({resolved_country}) added to blocklist")
                    socketio.emit('ip_blocked', {'ip': ip})

# -------------------
# Routes
# -------------------
@app.route("/")
def index(): return render_template("index.html")

@app.route("/dashboard")
def dashboard(): return render_template("dashboard.html")

@app.route("/simulate_request", methods=["POST"])
def simulate_request():
    ip = request.remote_addr or "127.0.0.1"
    return jsonify({"status": "ok", "ip": ip}), 200

@app.route("/unblock/<ip_to_unblock>")
def unblock(ip_to_unblock):
    with lock:
        if ip_to_unblock in blocked_ips:
            blocked_ips.remove(ip_to_unblock)
            print(f"[MANUAL-UNBLOCK] {ip_to_unblock} removed from blocklist.")
            socketio.emit('ip_unblocked', {'ip': ip_to_unblock})
            return f"<h1>Successfully unblocked {ip_to_unblock}</h1>", 200
        else:
            return f"<h1>IP {ip_to_unblock} was not in the blocklist.</h1>", 404

# -------------------
# Start server
# -------------------
if __name__ == "__main__":
    print("Starting Flask-SocketIO server with eventlet...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
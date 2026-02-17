from flask import Flask, render_template, request, redirect, jsonify
import requests
import json
import os
import time
import threading
from datetime import datetime

app = Flask(__name__)

DATA_FILE    = "websites.json"
PING_INTERVAL = 300  # 5 minutes

# ── Load sites ────────────────────────────────────────────────────────────────
if os.path.exists(DATA_FILE):
    with open(DATA_FILE) as f:
        websites = json.load(f)
else:
    websites = []

# Ensure all required fields exist on old data
for site in websites:
    site.setdefault("status", "Unknown")
    site.setdefault("last_ping", None)
    site.setdefault("response_time", None)
    site.setdefault("next_ping_in", PING_INTERVAL)
    site.setdefault("paused", False)
    site.setdefault("uptime_pct", 100.0)
    site.setdefault("history", [])

next_id = max([w["id"] for w in websites], default=0) + 1
lock    = threading.Lock()

# ── Helpers ───────────────────────────────────────────────────────────────────
def save_websites():
    with open(DATA_FILE, "w") as f:
        json.dump(websites, f, indent=4)

def calc_uptime(history):
    if not history:
        return 100.0
    up = sum(1 for h in history if h["status"] == "UP")
    return round((up / len(history)) * 100, 1)

def do_ping(site):
    start = time.time()
    try:
        r = requests.get(site["url"], timeout=10)
        elapsed_ms = round((time.time() - start) * 1000)
        status = "UP" if r.status_code < 400 else "DOWN"
    except Exception:
        elapsed_ms = None
        status = "DOWN"

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    site["status"]        = status
    site["last_ping"]     = now_str
    site["response_time"] = elapsed_ms
    site["next_ping_in"]  = PING_INTERVAL

    # Keep last 60 pings for uptime & history bar
    history = site.setdefault("history", [])
    history.append({"time": now_str, "status": status, "ms": elapsed_ms})
    if len(history) > 60:
        history.pop(0)

    site["uptime_pct"] = calc_uptime(history)

# ── Background pinger ─────────────────────────────────────────────────────────
def background_pinger():
    while True:
        time.sleep(1)
        with lock:
            for site in websites:
                if site.get("paused"):
                    continue
                site["next_ping_in"] = max(0, site.get("next_ping_in", PING_INTERVAL) - 1)
                if site["next_ping_in"] <= 0:
                    do_ping(site)
            save_websites()

threading.Thread(target=background_pinger, daemon=True).start()

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    with lock:
        return render_template("index.html", websites=list(websites))

# JS polls this every second
@app.route("/state")
def state():
    with lock:
        return jsonify([{
            "id":            s["id"],
            "url":           s["url"],
            "status":        s["status"],
            "last_ping":     s["last_ping"],
            "response_time": s["response_time"],
            "next_ping_in":  s["next_ping_in"],
            "paused":        s.get("paused", False),
            "uptime_pct":    s.get("uptime_pct", 100.0),
            "history":       s.get("history", [])[-30:]
        } for s in websites])

# Add monitor
@app.route("/add", methods=["POST"])
def add_website():
    global next_id
    url = request.form.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL"}), 400
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    with lock:
        if any(w["url"] == url for w in websites):
            return jsonify({"error": "Duplicate"}), 409
        new_site = {
            "id": next_id, "url": url,
            "status": "Checking", "last_ping": None,
            "response_time": None, "next_ping_in": 5,
            "paused": False, "uptime_pct": 100.0, "history": []
        }
        websites.append(new_site)
        next_id += 1
        save_websites()
    return jsonify({"id": new_site["id"], "url": url})

# Delete monitor
@app.route("/delete/<int:site_id>", methods=["GET","POST"])
def delete_website(site_id):
    global websites
    with lock:
        websites[:] = [w for w in websites if w["id"] != site_id]
        save_websites()
    return jsonify({"deleted": site_id})

# Manual ping
@app.route("/ping/<int:site_id>", methods=["GET","POST"])
def ping_website(site_id):
    with lock:
        site = next((w for w in websites if w["id"] == site_id), None)
        if not site:
            return jsonify({"error": "Not found"}), 404
        do_ping(site)
        save_websites()
        return jsonify({
            "id": site["id"], "status": site["status"],
            "last_ping": site["last_ping"],
            "response_time": site["response_time"],
            "uptime_pct": site["uptime_pct"]
        })

# Pause / Resume
@app.route("/pause/<int:site_id>", methods=["POST"])
def pause_monitor(site_id):
    with lock:
        site = next((w for w in websites if w["id"] == site_id), None)
        if not site:
            return jsonify({"error": "Not found"}), 404
        site["paused"] = not site.get("paused", False)
        if not site["paused"]:
            site["next_ping_in"] = 5  # ping soon after resume
        save_websites()
        return jsonify({"id": site_id, "paused": site["paused"]})

# Public status page
@app.route("/status")
def public_status():
    with lock:
        data = [{
            "url":        s["url"],
            "status":     s["status"],
            "uptime_pct": s.get("uptime_pct", 100.0),
            "last_ping":  s["last_ping"],
            "history":    s.get("history", [])[-30:],
            "paused":     s.get("paused", False)
        } for s in websites]
    return render_template("status.html", sites=data)

# GitHub Actions bulk check
@app.route("/run-check")
def run_check():
    with lock:
        results = []
        for site in websites:
            if not site.get("paused"):
                do_ping(site)
                results.append({"id": site["id"], "url": site["url"],
                                 "status": site["status"],
                                 "response_time": site["response_time"]})
        save_websites()
    return jsonify({"checked": len(results), "results": results})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
from flask import Flask, render_template, request, redirect, jsonify
import requests
import json
import os

app = Flask(__name__)

DATA_FILE = "websites.json"

# Load websites from file or initialize empty list
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        websites = json.load(f)
else:
    websites = []

# Determine next ID
next_id = max([w["id"] for w in websites], default=0) + 1

# Helper to save websites to file
def save_websites():
    with open(DATA_FILE, "w") as f:
        json.dump(websites, f, indent=4)

# Home page
@app.route("/")
def index():
    return render_template("index.html", websites=websites)

# Add a new website
@app.route("/add", methods=["POST"])
def add_website():
    global next_id
    url = request.form.get("url")
    if url:
        websites.append({
            "id": next_id,
            "url": url,
            "status": "Checking"
        })
        next_id += 1
        save_websites()
    return redirect("/")

# Delete a website
@app.route("/delete/<int:site_id>")
def delete_website(site_id):
    global websites
    websites = [w for w in websites if w["id"] != site_id]
    save_websites()
    return redirect("/")

# Ping a single website (manual or auto)
@app.route("/ping/<int:site_id>", methods=["GET"])
def ping_website(site_id):
    site = next((w for w in websites if w["id"] == site_id), None)
    if site:
        try:
            response = requests.get(site["url"], timeout=5)
            site["status"] = "UP" if response.status_code == 200 else "DOWN"
        except:
            site["status"] = "DOWN"
        save_websites()
        return jsonify({"status": site["status"]})
    return jsonify({"status": "Unknown"})

# Optional endpoint to ping all websites (used by GitHub Actions)
@app.route("/run-check", methods=["GET"])
def run_check():
    for site in websites:
        try:
            response = requests.get(site["url"], timeout=5)
            site["status"] = "UP" if response.status_code == 200 else "DOWN"
        except:
            site["status"] = "DOWN"
    save_websites()
    return "All websites checked!"

# Run Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

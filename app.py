from flask import Flask, render_template, request, redirect, jsonify
import requests

app = Flask(__name__)

# List of websites to monitor
websites = []
next_id = 1  # Auto-increment ID

# Home page - show all websites
@app.route("/")
def index():
    return render_template("index.html", websites=websites)

# Add new website
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
    return redirect("/")

# Delete website
@app.route("/delete/<int:site_id>")
def delete_website(site_id):
    global websites
    websites = [w for w in websites if w["id"] != site_id]
    return redirect("/")

# Ping a website (manual or API ping)
@app.route("/ping/<int:site_id>", methods=["GET"])
def ping_website(site_id):
    site = next((w for w in websites if w["id"] == site_id), None)
    if site:
        try:
            response = requests.get(site["url"], timeout=5)
            if response.status_code == 200:
                site["status"] = "UP"
            else:
                site["status"] = "DOWN"
        except:
            site["status"] = "DOWN"
        return jsonify({"status": site["status"]})
    return jsonify({"status": "Unknown"})

# Optional: endpoint to ping all websites (for GitHub Actions or cron)
@app.route("/run-check", methods=["GET"])
def run_check():
    for site in websites:
        try:
            response = requests.get(site["url"], timeout=5)
            site["status"] = "UP" if response.status_code == 200 else "DOWN"
        except:
            site["status"] = "DOWN"
    return "All websites checked!"

# Run app
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

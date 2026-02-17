import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

DATABASE = "database/models.db"
SECRET_KEY = "mysecret123"  # change this


# -----------------------------
# Create database if not exists
# -----------------------------
def init_db():
    if not os.path.exists("database"):
        os.makedirs("database")

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            status TEXT DEFAULT 'Unknown'
        )
    """)
    conn.commit()
    conn.close()


init_db()


# -----------------------------
# Home Page
# -----------------------------
@app.route("/")
def index():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sites")
    sites = cur.fetchall()
    conn.close()
    return render_template("index.html", sites=sites)


# -----------------------------
# Add Website
# -----------------------------
@app.route("/add", methods=["POST"])
def add_site():
    url = request.form["url"]

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("INSERT INTO sites (url, status) VALUES (?, ?)", (url, "Checking"))
    conn.commit()
    conn.close()

    return redirect("/")


# -----------------------------
# Delete Website
# -----------------------------
@app.route("/delete/<int:site_id>")
def delete_site(site_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("DELETE FROM sites WHERE id=?", (site_id,))
    conn.commit()
    conn.close()

    return redirect("/")


# -----------------------------
# Run Check (Called by GitHub)
# -----------------------------
@app.route("/run-check")
def run_check():
    key = request.args.get("key")
    if key != SECRET_KEY:
        return "Unauthorized", 403

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT id, url FROM sites")
    sites = cur.fetchall()

    for site_id, url in sites:
        try:
            r = requests.get(url, timeout=5)
            status = "UP" if r.status_code == 200 else "DOWN"
        except:
            status = "DOWN"

        cur.execute("UPDATE sites SET status=? WHERE id=?", (status, site_id))

    conn.commit()
    conn.close()

    return "Checked Successfully"


if __name__ == "__main__":
    app.run(debug=True)

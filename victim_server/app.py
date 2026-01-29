from flask import Flask, request, render_template, redirect, url_for
import datetime
import csv
import os

app = Flask(__name__)

# --- CONFIGURATION ---
LOG_FILE = 'access_logs.csv'
VALID_USER = "admin"
VALID_PASS = "secure123"  # The password the attacker is trying to guess

# Ensure log file exists with headers
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'ip_address', 'username', 'status'])

def log_attempt(ip, username, status):
    """Writes the login attempt to a CSV file for the ML model to read."""
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now(), ip, username, status])

@app.route('/', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        ip_address = request.remote_addr

        if username == VALID_USER and password == VALID_PASS:
            log_attempt(ip_address, username, "SUCCESS")
            return f"<h1>Welcome, {username}!</h1><p>You have successfully logged in.</p>"
        else:
            log_attempt(ip_address, username, "FAILED")
            message = "Invalid Credentials. Please try again."
    
    return render_template('login.html', message=message)

if __name__ == '__main__':
    # Run on 0.0.0.0 so it can be accessed by other machines/VMs
    app.run(host='0.0.0.0', port=5000, debug=True)
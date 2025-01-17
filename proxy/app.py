from flask import Flask, request, jsonify, send_file
import requests
import uuid
import os
import json
from threading import Thread
import time

app = Flask(__name__)

# Home Assistant API base URL and Supervisor token (injected by Home Assistant)
HA_BASE_URL = "http://supervisor/core/api"
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
    "Content-Type": "application/json",
}

# Path to store the token
TOKEN_FILE = "/data/long_lived_token.json"

# Token auto-renewal settings
TOKEN_NAME = "Auto-Renewed Token"
TOKEN_DURATION_DAYS = 365
RENEWAL_THRESHOLD_DAYS = 30  # Renew if less than 30 days remain


def load_token():
    """Load the token from the file."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            return json.load(file)
    return {}


def save_token(token_data):
    """Save the token to a file."""
    with open(TOKEN_FILE, "w") as file:
        json.dump(token_data, file)


def renew_token_if_needed():
    """Automatically renew the token if it is close to expiration."""
    while True:
        token_data = load_token()
        if token_data:
            expiration = token_data.get("expiration")
            if expiration and is_token_expiring_soon(expiration):
                generate_and_store_token()
        time.sleep(86400)  # Check daily


def is_token_expiring_soon(expiration):
    """Check if the token is expiring soon."""
    expiration_timestamp = int(expiration)
    current_timestamp = int(time.time())
    days_left = (expiration_timestamp - current_timestamp) / (24 * 3600)
    return days_left < RENEWAL_THRESHOLD_DAYS


def generate_and_store_token():
    """Generate a new long-lived token and store it."""
    response = requests.post(
        f"{HA_BASE_URL}/auth/long_lived_access_token",
        headers=HEADERS,
        json={"name": TOKEN_NAME, "expiration": f"{TOKEN_DURATION_DAYS}d"},
    )
    if response.status_code == 200:
        token_data = response.json()
        save_token(token_data)
        print(f"Token renewed: {token_data['token']}")
    else:
        print("Failed to renew token:", response.text)


@app.route("/entities", methods=["GET"])
def get_entities():
    """Fetch all entities from Home Assistant."""
    response = requests.get(f"{HA_BASE_URL}/states", headers=HEADERS)
    if response.status_code == 200:
        return jsonify(response.json()), 200
    return jsonify({"error": "Failed to fetch entities"}), response.status_code


@app.route("/mac", methods=["GET"])
def get_mac_address():
    """Get the MAC address of the device."""
    try:
        mac = hex(uuid.getnode())[2:].zfill(12).upper()
        mac_address = ":".join(mac[i:i+2] for i in range(0, 12, 2))
        return jsonify({"mac_address": mac_address}), 200
    except Exception as e:
        return jsonify({"error": "Failed to retrieve MAC address", "details": str(e)}), 500


@app.route("/token", methods=["GET"])
def get_token():
    """Retrieve the current token."""
    token_data = load_token()
    if token_data:
        return jsonify(token_data), 200
    return jsonify({"error": "No token found"}), 404


@app.route("/download", methods=["GET"])
def download_files():
    """Download the addon files as a ZIP."""
    zip_path = "/data/homeassistant-addon.zip"
    create_zip(zip_path)
    return send_file(zip_path, as_attachment=True)


def create_zip(output_path):
    """Create a ZIP file of the addon."""
    import zipfile

    addon_files = {
        "config.json": ADDON_CONFIG,
        "Dockerfile": DOCKERFILE_CONTENT,
        "proxy/app.py": open(__file__).read(),
        "proxy/requirements.txt": REQUIREMENTS_CONTENT,
    }

    with zipfile.ZipFile(output_path, "w") as zipf:
        for file_name, content in addon_files.items():
            zipf.writestr(file_name, content)


# Static content for the addon files
ADDON_CONFIG = """{
  "name": "Home Assistant Proxy",
  "version": "1.0.0",
  "slug": "ha_proxy",
  "description": "Proxy to expose all Home Assistant entities and control them",
  "arch": ["armv7", "arm64", "amd64", "i386"],
  "startup": "application",
  "boot": "auto",
  "ingress": false,
  "options": {},
  "schema": {},
  "ports": {
    "5000/tcp": 5000
  },
  "host_network": true
}
"""

DOCKERFILE_CONTENT = """FROM python:3.10-slim

RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY proxy/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY proxy/ .

CMD ["python", "app.py"]
"""

REQUIREMENTS_CONTENT = """flask
requests
"""

# Start the token renewal thread
Thread(target=renew_token_if_needed, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

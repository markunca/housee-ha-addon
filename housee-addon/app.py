from flask import Flask, jsonify, request
import os
import uuid
import json
from threading import Thread
import time

app = Flask(__name__)

# Path to store the secret token
TOKEN_FILE = "/data/secret_token.json"
SECRET_TOKEN = "default-token"  # Replace this with a securely generated token

# Load the token from a file (if it exists)
if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r") as file:
        SECRET_TOKEN = json.load(file).get("secret_token", SECRET_TOKEN)

# Auto-renewal for tokens (placeholder example)
def renew_token():
    while True:
        # Token renewal logic could be added here
        time.sleep(86400)  # Check daily


@app.before_request
def authenticate_request():
    """Authenticate incoming requests using a secret token."""
    token = request.headers.get("Authorization")
    if not token or token != f"Bearer {SECRET_TOKEN}":
        return jsonify({"error": "Unauthorized"}), 401


@app.route('/entities', methods=['GET'])
def get_entities():
    """Fetch all entities (placeholder response)."""
    return jsonify({"entities": "This is a placeholder for entity data."})


@app.route('/mac', methods=['GET'])
def get_mac():
    """Return a dummy MAC address."""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 2*6, 2)][::-1])
    return jsonify({"mac_address": mac})


@app.route('/token', methods=['GET'])
def get_token():
    """Retrieve the current token."""
    return jsonify({"token": SECRET_TOKEN})


@app.route('/generate_token', methods=['POST'])
def generate_token():
    """Generate a new token (only if authenticated)."""
    global SECRET_TOKEN
    SECRET_TOKEN = uuid.uuid4().hex
    with open(TOKEN_FILE, "w") as file:
        json.dump({"secret_token": SECRET_TOKEN}, file)
    return jsonify({"message": "New token generated", "token": SECRET_TOKEN})


if __name__ == "__main__":
    # Start a thread for token renewal (if needed in the future)
    Thread(target=renew_token, daemon=True).start()

    # Start the Flask app
    app.run(host="0.0.0.0", port=5000)

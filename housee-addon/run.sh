#!/usr/bin/env bash

echo "Starting Housee Add-on..."

# Start a basic Flask app for API communication
cat <<EOF > /app/app.py
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/entities', methods=['GET'])
def get_entities():
    return jsonify({"message": "This endpoint will return all entities."})

@app.route('/mac', methods=['GET'])
def get_mac():
    mac = ':'.join(['{:02x}'.format((os.getpid() >> ele) & 0xff) for ele in range(0, 2*6, 2)][::-1])
    return jsonify({"mac_address": mac})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Run the Python app
python3 /app/app.py

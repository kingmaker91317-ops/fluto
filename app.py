import os
import json
import re
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)
DB_FILE = 'keys.json'

def load_keys():
    if not os.path.exists(DB_FILE):
        default_data = {
            "MY-VIP-KEY-2026": {
                "plan": "VIP Lifetime",
                "expiry": "2099-12-31 23:59:59",
                "hwid": None,
                "status": "active"
            },
            "123456": {
                "plan": "VIP Lifetime",
                "expiry": "2099-12-31 23:59:59",
                "hwid": None,
                "status": "active"
            }
        }
        return default_data

    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_keys(keys_data):
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(keys_data, f, indent=4)
    except Exception:
        pass

# ==================== WEB DASHBOARD ROUTES ====================

@app.route('/')
def dashboard():
    keys_data = load_keys()
    return render_template('index.html', keys=keys_data)

@app.route('/add_key', methods=['POST'])
def add_key():
    key = request.form.get('key', '').strip()
    plan = request.form.get('plan', 'VIP Lifetime').strip()
    expiry = request.form.get('expiry', '2099-12-31 23:59:59').strip()
    
    if key:
        keys_data = load_keys()
        keys_data[key] = {
            "plan": plan,
            "expiry": expiry,
            "hwid": None,
            "status": "active"
        }
        save_keys(keys_data)
    return redirect(url_for('dashboard'))

@app.route('/delete_key/<key>')
def delete_key(key):
    keys_data = load_keys()
    if key in keys_data:
        del keys_data[key]
        save_keys(keys_data)
    return redirect(url_for('dashboard'))

@app.route('/toggle_key/<key>')
def toggle_key(key):
    keys_data = load_keys()
    if key in keys_data:
        current_status = keys_data[key].get('status', 'active')
        keys_data[key]['status'] = 'paused' if current_status == 'active' else 'active'
        save_keys(keys_data)
    return redirect(url_for('dashboard'))

@app.route('/reset_hwid/<key>')
def reset_hwid(key):
    keys_data = load_keys()
    if key in keys_data:
        keys_data[key]['hwid'] = None
        save_keys(keys_data)
    return redirect(url_for('dashboard'))

# ==================== FLUORITE API ENDPOINT ====================

@app.route('/api/v1/software/init', methods=['POST', 'GET'])
@app.route('/api/v1/software/init/', methods=['POST', 'GET'])
@app.route('/api/v1/software/a/init', methods=['POST', 'GET'])
@app.route('/api/v1/software/a/init/', methods=['POST', 'GET'])
def client_init():
    if request.method == 'GET':
        return jsonify({"status": "online", "message": "Fluorite Server is running!"})

    response = jsonify({
        "status": "success",
        "success": True,
        "plan": "VIP Lifetime",
        "expiry": "2099-12-31 23:59:59",
        "min_version": "1.0",
        "latest_version": "1.0",
        "message": "Authentication Successful",
        "is_super_license": True,
        "is_banned": False,
        "ban_reason": ""
    })
    response.headers['X-Emerite-Sig'] = 'true'
    return response, 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=True)

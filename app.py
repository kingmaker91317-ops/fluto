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
        try:
            with open(DB_FILE, 'w') as f:
                json.dump(default_data, f, indent=4)
        except Exception:
            pass
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
def client_init():
    if request.method == 'GET':
        return jsonify({"status": "online", "message": "Fluorite Server is running!"})

    raw_body = request.get_data(as_text=True) or ''
    json_data = request.get_json(silent=True) or {}
    form_data = request.form or {}
    args_data = request.args or {}

    # Extract license key from any source
    key = (
        json_data.get('license_key') or
        json_data.get('key') or
        form_data.get('license_key') or
        form_data.get('key') or
        args_data.get('license_key') or
        args_data.get('key') or
        ''
    ).strip()

    # Regex extraction fallback if raw body was sent
    if not key and raw_body:
        match = re.search(r'(?:license_key|key|license)["\']?\s*[:=]\s*["\']?([^"\'&\s,{}]+)', raw_body, re.IGNORECASE)
        if match:
            key = match.group(1).strip()
        elif len(raw_body.strip()) > 0 and len(raw_body.strip()) < 50 and not raw_body.startswith('{'):
            key = raw_body.strip()

    client_hwid = (
        json_data.get('hwid') or
        form_data.get('hwid') or
        args_data.get('hwid') or
        ''
    )
    if not client_hwid and raw_body:
        hwid_match = re.search(r'hwid["\']?\s*[:=]\s*["\']?([^"\'&\s,{}]+)', raw_body, re.IGNORECASE)
        if hwid_match:
            client_hwid = hwid_match.group(1).strip()

    keys_data = load_keys()

    # Auto-register key if non-empty and not present
    if key and key not in keys_data:
        keys_data[key] = {
            "plan": "VIP Lifetime",
            "expiry": "2099-12-31 23:59:59",
            "hwid": client_hwid if client_hwid else None,
            "status": "active"
        }
        save_keys(keys_data)

    # If key is in keys_data, check status & hwid
    if key and key in keys_data:
        key_info = keys_data[key]
        if key_info.get('status') == 'paused':
            response = jsonify({
                "status": "failed",
                "success": False,
                "message": "License key is currently paused."
            })
            response.headers['X-Emerite-Sig'] = 'true'
            return response, 200

        # Update HWID if not set
        if not key_info.get('hwid') and client_hwid:
            key_info['hwid'] = client_hwid
            save_keys(keys_data)

        plan = key_info.get('plan', 'VIP Lifetime')
        expiry = key_info.get('expiry', '2099-12-31 23:59:59')
    else:
        # Universal Fallback: Accept any request gracefully with VIP Lifetime
        plan = "VIP Lifetime"
        expiry = "2099-12-31 23:59:59"

    # Always return Auth Success Response
    response = jsonify({
        "status": "success",
        "success": True,
        "plan": plan,
        "expiry": expiry,
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

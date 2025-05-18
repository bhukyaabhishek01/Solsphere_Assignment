from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)
db = {}  # In-memory DB: {machine_id: {timestamp, status}}

@app.route('/report', methods=['POST'])
def report():
    data = request.json
    machine_id = data.get('machine_id')
    db[machine_id] = data
    return jsonify({"status": "received"}), 200

@app.route('/machines', methods=['GET'])
def list_machines():
    return jsonify([{
        "machine_id": mid,
        "last_checkin": status['timestamp'],
        **status
    } for mid, status in db.items()])

@app.route('/export', methods=['GET'])
def export_csv():
    import csv
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["machine_id", "timestamp", "os", "disk_encryption", "os_update_status", "antivirus", "sleep_setting"])
    for mid, status in db.items():
        writer.writerow([mid, status['timestamp'], status['os'], status['disk_encryption'], status['os_update_status'], status['antivirus'], status['sleep_setting']])
    return si.getvalue(), 200, {"Content-Type": "text/csv"}

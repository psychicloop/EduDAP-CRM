
# edudap-office/app/portal.py
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone

# Blueprint for the main portal area
portal_bp = Blueprint('portal', __name__, url_prefix='/app')

@portal_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    Endpoint: portal.dashboard
    URL: /app/dashboard
    """
    return render_template('dashboard.html')

@portal_bp.route('/attendance', methods=['GET'])
@login_required
def attendance_page():
    """
    Endpoint: portal.attendance_page
    URL: /app/attendance
    Renders the attendance UI page.
    """
    return render_template('attendance.html')

@portal_bp.route('/attendance/punch', methods=['POST'])
@login_required
def attendance_punch():
    """
    Endpoint: portal.attendance_punch
    URL: /app/attendance/punch
    Accepts POST from the Attendance page and returns JSON.
    """
    # Accept both application/x-www-form-urlencoded and JSON inputs
    status = request.form.get('status') or (request.json.get('status') if request.is_json else None)
    if not status:
        status = 'punch'  # default label if client didn’t send anything

    now = datetime.now(timezone.utc).isoformat()
    user_id = getattr(current_user, "id", None)  # won't break if current_user has no 'id'

    # TODO: Save punch to your DB here (left as-is to keep this file generic)

    return jsonify({
        "ok": True,
        "status": status,
        "user_id": user_id,
        "timestamp": now
    }), 200

# Optional: simple root redirect so /app goes to dashboard
@portal_bp.route('/', methods=['GET'])
@login_required
def portal_root():
    return redirect(url_for('portal.dashboard'))

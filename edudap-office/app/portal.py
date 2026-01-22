
# edudap-office/app/portal.py
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone

# Portal blueprint
portal_bp = Blueprint('portal', __name__, url_prefix='/app')

# ---------- Core Navigation ----------

@portal_bp.route('/', methods=['GET'])
@login_required
def portal_root():
    # Redirect /app → /app/dashboard
    return redirect(url_for('portal.dashboard'))

@portal_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Endpoint: portal.dashboard"""
    return render_template('dashboard.html')

@portal_bp.route('/attendance', methods=['GET'])
@login_required
def attendance_page():
    """Endpoint: portal.attendance_page"""
    return render_template('attendance.html')

@portal_bp.route('/leads', methods=['GET'])
@login_required
def leads_page():
    """Endpoint: portal.leads_page"""
    return render_template('leads.html')

@portal_bp.route('/students', methods=['GET'])
@login_required
def students_page():
    """Endpoint: portal.students_page"""
    return render_template('students.html')

@portal_bp.route('/fees', methods=['GET'])
@login_required
def fees_page():
    """Endpoint: portal.fees_page"""
    return render_template('fees.html')

@portal_bp.route('/tasks', methods=['GET'])
@login_required
def tasks_page():
    """Endpoint: portal.tasks_page"""
    return render_template('tasks.html')

@portal_bp.route('/reports', methods=['GET'])
@login_required
def reports_page():
    """Endpoint: portal.reports_page"""
    return render_template('reports.html')

@portal_bp.route('/settings', methods=['GET'])
@login_required
def settings_page():
    """Endpoint: portal.settings_page"""
    return render_template('settings.html')

@portal_bp.route('/profile', methods=['GET'])
@login_required
def profile_page():
    """Endpoint: portal.profile_page"""
    return render_template('profile.html')

# ---------- Attendance API (AJAX) ----------

@portal_bp.route('/attendance/punch', methods=['POST'])
@login_required
def attendance_punch():
    """
    Endpoint: portal.attendance_punch
    Accepts POST { status: 'in' | 'out' } and returns JSON.
    """
    status = request.form.get('status') or (request.json.get('status') if request.is_json else None)
    if not status:
        status = 'punch'

    now = datetime.now(timezone.utc).isoformat()
    user_id = getattr(current_user, "id", None)

    # TODO: Persist to DB if needed
    return jsonify({
        "ok": True,
        "status": status,
        "user_id": user_id,
        "timestamp": now
    }), 200
``

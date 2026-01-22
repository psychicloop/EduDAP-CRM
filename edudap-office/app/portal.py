
# edudap-office/app/portal.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

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
    """
    return render_template('attendance.html')

# Optional: simple root redirect so /app goes to dashboard
@portal_bp.route('/', methods=['GET'])
@login_required
def portal_root():
    return redirect(url_for('portal.dashboard'))

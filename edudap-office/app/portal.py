
# edudap-office/app/portal.py
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone

portal_bp = Blueprint('portal', __name__, url_prefix='/app')

# ---------- Root / Dashboard ----------
@portal_bp.route('/', methods=['GET'])
@login_required
def portal_root():
    return redirect(url_for('portal.dashboard'))

@portal_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    stats = {
        "leads": 28,
        "students": 143,
        "fees_today": "₹1,24,500",
        "pending_tasks": 7
    }
    notices = [
        {"title": "Admissions Week", "desc": "Special drive from Mon–Fri", "badge": "info"},
        {"title": "PTM Schedule", "desc": "Parent meetings this Saturday", "badge": "primary"},
        {"title": "Fee Reminder", "desc": "Auto reminders sent at 6 PM", "badge": "warning"}
    ]
    return render_template('dashboard.html', stats=stats, notices=notices)

# ---------- Attendance ----------
@portal_bp.route('/attendance', methods=['GET'])
@login_required
def attendance_page():
    history = [
        {"when": "2026-01-20 09:02", "type": "in"},
        {"when": "2026-01-20 18:07", "type": "out"},
        {"when": "2026-01-21 09:11", "type": "in"},
        {"when": "2026-01-21 18:02", "type": "out"},
    ]
    return render_template('attendance.html', history=history)

@portal_bp.route('/attendance/punch', methods=['POST'])
@login_required
def attendance_punch():
    status = request.form.get('status') or (request.json.get('status') if request.is_json else None)
    if not status:
        status = 'punch'
    now = datetime.now(timezone.utc).isoformat()
    user_id = getattr(current_user, "id", None)
    # TODO: persist to DB as needed
    return jsonify({"ok": True, "status": status, "user_id": user_id, "timestamp": now}), 200

# ---------- Leads ----------
@portal_bp.route('/leads', methods=['GET'])
@login_required
def leads_page():
    leads = [
        {"id": 1, "name": "Alice Singh", "source": "Website", "status": "New", "updated": "2026-01-20"},
        {"id": 2, "name": "Rohit Kumar", "source": "Referral", "status": "Contacted", "updated": "2026-01-21"},
        {"id": 3, "name": "Neha Gupta", "source": "Facebook", "status": "Qualified", "updated": "2026-01-21"},
    ]
    return render_template('leads.html', leads=leads)

# ---------- Students ----------
@portal_bp.route('/students', methods=['GET'])
@login_required
def students_page():
    students = [
        {"id": "STU-001", "name": "Karan Mehta", "course": "B.Sc. Physics", "batch": "2025", "status": "Active"},
        {"id": "STU-002", "name": "Priya Nair", "course": "B.A. Economics", "batch": "2024", "status": "Active"},
        {"id": "STU-003", "name": "Amit Sharma", "course": "BCA", "batch": "2025", "status": "On Hold"},
    ]
    return render_template('students.html', students=students)

# ---------- Fees ----------
@portal_bp.route('/fees', methods=['GET'])
@login_required
def fees_page():
    payments = [
        {"receipt": "RCPT-1001", "student": "Karan Mehta", "amount": 35000, "mode": "UPI", "date": "2026-01-20"},
        {"receipt": "RCPT-1002", "student": "Priya Nair", "amount": 50000, "mode": "Card", "date": "2026-01-21"},
        {"receipt": "RCPT-1003", "student": "Amit Sharma", "amount": 15000, "mode": "Cash", "date": "2026-01-21"},
    ]
    totals = {"today": "₹1,00,000", "month": "₹8,75,000", "pending": "₹2,10,000"}
    return render_template('fees.html', payments=payments, totals=totals)

# ---------- Tasks ----------
@portal_bp.route('/tasks', methods=['GET'])
@login_required
def tasks_page():
    tasks = [
        {"id": "T-101", "title": "Call back Alice", "due": "2026-01-22", "priority": "High", "status": "Open"},
        {"id": "T-102", "title": "Upload fee report", "due": "2026-01-23", "priority": "Medium", "status": "In Progress"},
        {"id": "T-103", "title": "Schedule seminar", "due": "2026-01-25", "priority": "Low", "status": "Open"},
    ]
    return render_template('tasks.html', tasks=tasks)

# ---------- Reports ----------
@portal_bp.route('/reports', methods=['GET'])
@login_required
def reports_page():
    chart = {
        "labels": ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"],
        "admissions": [24, 31, 37, 40, 29, 43],
        "revenue": [450000, 580000, 630000, 700000, 520000, 820000]
    }
    return render_template('reports.html', chart=chart)

# ---------- Settings ----------
@portal_bp.route('/settings', methods=['GET'])
@login_required
def settings_page():
    org = {"name": "EduDAP", "email": "info@edudap.org", "phone": "+91-99999-00000"}
    return render_template('settings.html', org=org)

# ---------- Profile ----------
@portal_bp.route('/profile', methods=['GET'])
@login_required
def profile_page():
    profile = {
        "name": getattr(current_user, "name", "User"),
        "email": getattr(current_user, "email", "user@example.com"),
        "role": getattr(current_user, "role", "Staff")
    }
    return render_template('profile.html', profile=profile)


from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import date
from .models import User, LeaveRequest, Expense, Task, Attendance
from . import db

admin_bp = Blueprint('admin', __name__)

# Admin guard
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'Admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('portal.dashboard'))
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.count()
    leaves_pending = LeaveRequest.query.filter_by(status='Pending').count()
    expenses_count = Expense.query.count()
    active = Attendance.query.filter(Attendance.day==date.today(), Attendance.in_time!=None, Attendance.out_time==None).count()  # noqa
    return render_template('admin_dashboard.html', users=users, leaves_pending=leaves_pending, expenses_count=expenses_count, active=active)

# Manage Users
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.role.desc()).all()
    return render_template('manage_users.html', users=all_users)

@admin_bp.route('/users/<int:user_id>/promote', methods=['POST'])
@login_required
@admin_required
def promote(user_id):
    u = User.query.get_or_404(user_id)
    u.role = 'Admin'
    db.session.commit()
    flash('Promoted to Admin.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/demote', methods=['POST'])
@login_required
@admin_required
def demote(user_id):
    u = User.query.get_or_404(user_id)
    if u.id == current_user.id:
        flash('You cannot demote yourself.', 'warning')
        return redirect(url_for('admin.users'))
    u.role = 'Employee'
    db.session.commit()
    flash('Demoted to Employee.', 'success')
    return redirect(url_for('admin.users'))

# Leaves moderation
@admin_bp.route('/leaves')
@login_required
@admin_required
def leaves():
    items = LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()
    return render_template('admin_leaves.html', items=items)

@admin_bp.route('/leaves/<int:leave_id>/<action>', methods=['POST'])
@login_required
@admin_required
def leaves_action(leave_id, action):
    lr = LeaveRequest.query.get_or_404(leave_id)
    if action not in ('approve','reject'):
        flash('Invalid action.', 'danger')
        return redirect(url_for('admin.leaves'))
    lr.status = 'Approved' if action=='approve' else 'Rejected'
    db.session.commit()
    flash(f'Leave {lr.status}.', 'success')
    return redirect(url_for('admin.leaves'))

# Expenses moderation (list-only sample)
@admin_bp.route('/expenses')
@login_required
@admin_required
def expenses():
    items = Expense.query.order_by(Expense.created_at.desc()).all()
    return render_template('admin_expenses.html', items=items)

# Assign tasks to users
@admin_bp.route('/assign', methods=['GET','POST'])
@login_required
@admin_required
def assign():
    users = User.query.order_by(User.username.asc()).all()
    if request.method == 'POST':
        title = request.form.get('title')
        details = request.form.get('details')
        priority = request.form.get('priority')
        assigned_to = request.form.get('assigned_to', type=int)
        due_at = request.form.get('due_at')
        t = Task(title=title, details=details, priority=priority or 'Normal', is_personal=False,
                 created_by=current_user.id, assigned_to=assigned_to, due_at=due_at or None)
        db.session.add(t)
        db.session.commit()
        flash('Task assigned.', 'success')
        return redirect(url_for('admin.assign'))
    tasks = Task.query.filter_by(is_personal=False).order_by(Task.created_at.desc()).all()
    return render_template('admin_assign.html', users=users, tasks=tasks)

# Live attendance locations (map)
@admin_bp.route('/attendance/live')
@login_required
@admin_required
def attendance_live():
    return render_template('admin_attendance_live.html')

@admin_bp.route('/api/attendance/live')
@login_required
@admin_required
def api_attendance_live():
    recs = Attendance.query.filter(Attendance.day==date.today(), Attendance.in_time!=None, Attendance.out_time==None).all()  # noqa
    data = []
    for r in recs:
        u = User.query.get(r.user_id)
        data.append({'username': u.username if u else 'User', 'lat': r.in_lat, 'lng': r.in_lng, 'in_time': r.in_time.isoformat()})
    return jsonify({'results': data})

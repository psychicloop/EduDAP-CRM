
import io
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from .models import Upload, ProductData, Attendance, LeaveRequest, Expense, Task, User
from . import db

portal_bp = Blueprint('portal', __name__)

# -------- Dashboard with Smart Search (tabs: Search, Upload) --------
@portal_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Search API (as-you-type)
@portal_bp.route('/api/search')
@login_required
def api_search():
    q = (request.args.get('q') or '').strip()
    results = []
    if len(q) >= 2:
        # very simple normalization & partial matching across item_description/make/brand/cat_no
        like = f"%{q}%"
        items = ProductData.query.filter(or_(
            ProductData.item_description.ilike(like),
            ProductData.make.ilike(like),
            ProductData.brand.ilike(like),
            ProductData.cat_no.ilike(like)
        )).limit(25).all()
        for p in items:
            results.append({
                'item_description': p.item_description,
                'make': p.make,
                'brand': p.brand,
                'cat_no': p.cat_no,
                'rate': p.rate
            })
    return jsonify({'results': results})

# Upload handler (Excel/CSV/PDF) from the Upload tab
@portal_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    f = request.files.get('file')
    if not f or f.filename == '':
        flash('Please choose a file.', 'danger')
        return redirect(url_for('portal.dashboard'))

    filename = f.filename
    ext = filename.lower().rsplit('.', 1)[-1]
    upload = Upload(user_id=current_user.id, filename=filename, filetype=ext)
    db.session.add(upload)
    db.session.flush()  # get upload.id before commit

    try:
        if ext in ('csv',):
            df = pd.read_csv(f)
            _ingest_dataframe(df, upload.id)
        elif ext in ('xlsx', 'xls'):  # requires openpyxl/xlrd
            df = pd.read_excel(f, engine='openpyxl')
            _ingest_dataframe(df, upload.id)
        elif ext in ('pdf',):
            # read pdf text and split by lines
            reader = PdfReader(f)
            lines = []
            for page in reader.pages:
                text = page.extract_text() or ''
                for line in text.split('
'):
                    line = line.strip()
                    if line:
                        lines.append(line)
            for line in lines:
                pd_row = ProductData(item_description=line[:512], upload_id=upload.id)
                db.session.add(pd_row)
        else:
            flash('Unsupported file type. Use CSV, XLSX or PDF.', 'warning')
            db.session.rollback()
            return redirect(url_for('portal.dashboard'))

        db.session.commit()
        flash('File uploaded and indexed for search.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Upload failed: {e}', 'danger')

    return redirect(url_for('portal.dashboard'))


def _ingest_dataframe(df, upload_id):
    # Normalize column names
    cols = {c.lower().strip(): c for c in df.columns}
    # Try common mappings
    def pick(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None
    c_item = pick('item_description','description','item','name','product')
    c_make = pick('make','manufacturer','mfg','brand')
    c_brand = pick('brand','make')
    c_cat = pick('cat_no','catalog','catalog_no','sku','code','part','part_no')
    c_rate = pick('rate','price','amount','value','mrp')

    for _, row in df.iterrows():
        item = str(row.get(c_item, '')).strip() if c_item else ''
        if not item:
            continue
        p = ProductData(
            item_description=item[:512],
            make=(str(row.get(c_make, '')).strip() if c_make else None),
            brand=(str(row.get(c_brand, '')).strip() if c_brand else None),
            cat_no=(str(row.get(c_cat, '')).strip() if c_cat else None),
            rate=float(row.get(c_rate)) if c_rate and pd.notna(row.get(c_rate)) else None,
            upload_id=upload_id
        )
        db.session.add(p)

# -------- Attendance (Punch In/Out with geolocation) --------
@portal_bp.route('/attendance')
@login_required
def attendance_page():
    # Show today's record for the user
    rec = Attendance.query.filter_by(user_id=current_user.id, day=date.today()).first()
    return render_template('attendance.html', record=rec)

@portal_bp.route('/attendance/punch', methods=['POST'])
@login_required
def attendance_punch():
    action = request.form.get('action')  # 'in' or 'out'
    lat = request.form.get('lat', type=float)
    lng = request.form.get('lng', type=float)
    if lat is None or lng is None:
        return jsonify({'ok': False, 'error': 'Location required'}), 400

    rec = Attendance.query.filter_by(user_id=current_user.id, day=date.today()).first()
    if not rec:
        rec = Attendance(user_id=current_user.id)
        db.session.add(rec)

    now = datetime.utcnow()
    if action == 'in' and rec.in_time is None:
        rec.in_time, rec.in_lat, rec.in_lng = now, lat, lng
    elif action == 'out' and rec.in_time is not None and rec.out_time is None:
        rec.out_time, rec.out_lat, rec.out_lng = now, lat, lng
    else:
        return jsonify({'ok': False, 'error': 'Invalid state'}), 400

    db.session.commit()
    return jsonify({'ok': True})

# -------- Leaves --------
@portal_bp.route('/leaves', methods=['GET', 'POST'])
@login_required
def leaves():
    if request.method == 'POST':
        leave_type = request.form.get('leave_type')
        reason = request.form.get('reason')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        lr = LeaveRequest(
            user_id=current_user.id,
            leave_type=leave_type,
            reason=reason,
            start_date=start_date,
            end_date=end_date,
            status='Pending')
        db.session.add(lr)
        db.session.commit()
        flash('Leave applied.', 'success')
        return redirect(url_for('portal.leaves'))

    my_leaves = LeaveRequest.query.filter_by(user_id=current_user.id).order_by(LeaveRequest.created_at.desc()).all()
    return render_template('leaves.html', leaves=my_leaves)

# -------- Expenses --------
@portal_bp.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    if request.method == 'POST':
        category = request.form.get('category')
        amount = request.form.get('amount', type=float)
        expense_date = request.form.get('expense_date')
        note = request.form.get('note')
        ex = Expense(user_id=current_user.id, category=category, amount=amount, expense_date=expense_date, note=note)
        db.session.add(ex)
        db.session.commit()
        flash('Expense submitted.', 'success')
        return redirect(url_for('portal.expenses'))

    items = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.created_at.desc()).all()
    return render_template('expenses.html', items=items)

# -------- Tasks: personal to-do + assigned tasks --------
@portal_bp.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    if request.method == 'POST':
        title = request.form.get('title')
        details = request.form.get('details')
        priority = request.form.get('priority')
        due_at = request.form.get('due_at')
        reminder_at = request.form.get('reminder_at')
        t = Task(title=title, details=details, priority=priority or 'Normal',
                 due_at=due_at or None, reminder_at=reminder_at or None,
                 is_personal=True, created_by=current_user.id, assigned_to=current_user.id)
        db.session.add(t)
        db.session.commit()
        flash('To-do created.', 'success')
        return redirect(url_for('portal.tasks'))

    my_tasks = Task.query.filter_by(assigned_to=current_user.id).order_by(Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=my_tasks)

@portal_bp.route('/tasks/<int:task_id>/status', methods=['POST'])
@login_required
def task_status(task_id):
    status = request.form.get('status')
    t = Task.query.get_or_404(task_id)
    if t.assigned_to != current_user.id and t.created_by != current_user.id:
        return jsonify({'ok': False, 'error': 'Not allowed'}), 403
    t.status = status
    db.session.commit()
    return jsonify({'ok': True})

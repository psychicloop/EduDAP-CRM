
import pandas as pd
from PyPDF2 import PdfReader
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from .models import Upload, ProductData, Attendance, LeaveRequest, Expense, Task
from . import db

portal_bp = Blueprint('portal', __name__)

# -------- Dashboard with Smart Search (tabs: Search, Upload) --------
@portal_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# -------- Live Search API (as-you-type) --------
@portal_bp.route('/api/search')
@login_required
def api_search():
    q = (request.args.get('q') or '').strip()
    results = []
    if len(q) >= 2:
        # partial matching across item_description, make, brand, cat_no
        like = f"%{q}%"
        items = ProductData.query.filter(
            or_(
                ProductData.item_description.ilike(like),
                ProductData.make.ilike(like),
                ProductData.brand.ilike(like),
                ProductData.cat_no.ilike(like),
            )
        ).limit(25).all()
        for p in items:
            results.append(
                {
                    "item_description": p.item_description,
                    "make": p.make,
                    "brand": p.brand,
                    "cat_no": p.cat_no,
                    "rate": p.rate,
                }
            )
    return jsonify({"results": results})

# -------- Upload (CSV / XLSX / PDF) --------
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
    # Your original code inside the try block
    pass
except Exception as e:
    # Prevent the app from crashing during deployment
    print(f"An error occurred in portal.py: {e}")

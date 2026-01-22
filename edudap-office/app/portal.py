
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

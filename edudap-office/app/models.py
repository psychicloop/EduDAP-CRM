
from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='Employee')  # Admin or Employee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Uploaded files tracking
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename = db.Column(db.String(255), nullable=False)
    filetype = db.Column(db.String(20))  # pdf/csv/xlsx
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# Searchable product/line items extracted from uploads
class ProductData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_description = db.Column(db.String(512), nullable=False)
    make = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    cat_no = db.Column(db.String(100))
    rate = db.Column(db.Float)
    upload_id = db.Column(db.Integer, db.ForeignKey('upload.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Attendance
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.Date, default=date.today, index=True)
    in_time = db.Column(db.DateTime)
    in_lat = db.Column(db.Float)
    in_lng = db.Column(db.Float)
    out_time = db.Column(db.DateTime)
    out_lat = db.Column(db.Float)
    out_lng = db.Column(db.Float)

# Leaves
class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leave_type = db.Column(db.String(50))
    reason = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Pending')  # Pending/Approved/Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Expenses
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50))
    amount = db.Column(db.Float)
    expense_date = db.Column(db.Date)
    note = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Tasks (personal to-do or admin assigned)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    details = db.Column(db.String(1000))
    priority = db.Column(db.String(20), default='Normal')  # Low/Normal/High/Critical
    status = db.Column(db.String(20), default='Todo')      # Todo/In Progress/Done
    due_at = db.Column(db.DateTime)
    reminder_at = db.Column(db.DateTime)
    is_personal = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

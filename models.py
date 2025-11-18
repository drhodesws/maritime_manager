# models.py — FINAL & 100% WORKING
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import g

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    employee_full_name = db.Column(db.String(100))
    permissions = db.Column(db.Text)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.Column(db.Text)
    users = db.relationship('User', backref='role_ref')

def generate_job_number():
    now = datetime.now()
    prefix = now.strftime("%m%y")
    last_job = Job.query.filter(Job.job_number.like(f"{prefix}%")).order_by(Job.job_number.desc()).first()
    seq = 1
    if last_job:
        seq = int(last_job.job_number[-4:]) + 1
    return f"{prefix}{seq:04d}"

def generate_po_number():
    now = datetime.now()
    prefix = now.strftime("%m%y")
    last_po = PurchaseOrder.query.filter(PurchaseOrder.order_number.like(f"{prefix}%")).order_by(PurchaseOrder.order_number.desc()).first()
    seq = 1
    if last_po:
        seq = int(last_po.order_number[-4:]) + 1
    return f"{prefix}{seq:04d}"

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    job_number = db.Column(db.String(8), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    scheduled_date = db.Column(db.Date, nullable=False)
    requested_service = db.Column(db.Text)
    vessel_id = db.Column(db.Integer, db.ForeignKey('vessels.id'))
    location = db.Column(db.String(200))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    
    vessel = db.relationship('Vessel', backref='jobs')
    customer = db.relationship('Customer', backref='jobs')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.job_number:
            self.job_number = generate_job_number()

    def __repr__(self):
        return f"<Job {self.job_number}>"

class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(8), unique=True, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    quantity = db.Column(db.Integer)
    item_description = db.Column(db.Text)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    notes = db.Column(db.Text)

    vendor = db.relationship('Vendor', backref='purchase_orders')
    customer = db.relationship('Customer', backref='purchase_orders')
    job = db.relationship('Job', backref='purchase_orders')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.order_number:
            self.order_number = generate_po_number()
        if 'created_by' not in kwargs and hasattr(g, 'current_user'):
            self.created_by = g.current_user.username

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    contact_info = db.Column(db.String(200))
    address = db.Column(db.String(200))
    hire_date = db.Column(db.Date)
    role_position = db.Column(db.String(100))
    payrate_rt = db.Column(db.Float)
    payrate_ot = db.Column(db.Float)
    stcw_certification = db.Column(db.String(100))
    twic_card = db.Column(db.String(20))
    merchant_mariner_credential_mmc = db.Column(db.String(20))
    years_of_experience = db.Column(db.String(10))

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200))
    company = db.Column(db.String(100))
    role = db.Column(db.String(50))

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)

class Timebook(db.Model):
    __tablename__ = 'timebooks'
    id = db.Column(db.Integer, primary_key=True)
    employee = db.Column(db.String(100))
    description = db.Column(db.String(200))
    time_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    stop_time = db.Column(db.Time)
    job_number = db.Column(db.String(10))
    mileage = db.Column(db.Integer)
    location = db.Column(db.String(100))
    billable = db.Column(db.String(3))
    pay_rate_rt = db.Column(db.Float)
    pay_rate_ot = db.Column(db.Float)
    paid = db.Column(db.Boolean, default=False)

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(200))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))

class Vessel(db.Model):
    __tablename__ = 'vessels'
    id = db.Column(db.Integer, primary_key=True)
    vessel_name = db.Column(db.String(100), nullable=False)
    imo_number = db.Column(db.String(20), unique=True)
    build_year = db.Column(db.Integer)
    vessel_type = db.Column(db.String(50))
    gross_tonnage_gt = db.Column(db.Float)
    flag_state = db.Column(db.String(50))
    uscg_documentation = db.Column(db.String(50))
    radar_system = db.Column(db.String(100))
    route_type = db.Column(db.String(50))

    def __repr__(self):
        return f"<Vessel {self.vessel_name}>"
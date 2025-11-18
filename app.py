# app.py — FINAL & WORKING
from flask import Flask, render_template, request, session, redirect, url_for, current_app
from config import Config
from models import db, User
from datetime import datetime
import json
import ast
from flask_migrate import Migrate
import os

# CREATE APP FIRST
app = Flask(__name__)
app.config.from_object(Config)

# Set absolute path for the existing database in the instance folder
project_dir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(project_dir, 'instance')
db_path = os.path.join(instance_path, 'maritime_manager.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Global login enforcement
@app.before_request
def require_login():
    if request.endpoint and request.endpoint not in ('auth.login', 'static') and 'username' not in session:
        return redirect(url_for('auth.login'))

# Now register blueprints (AFTER app is created!)
from routes.items import items_bp
from routes.auth import auth_bp
from routes.employees import employees_bp
from routes.timebooks import timebooks_bp
from routes.control_panel import control_panel_bp
from routes.contacts import contacts_bp
from routes.customers import customers_bp
from routes.jobs import jobs_bp
from routes.purchase_orders import purchase_orders_bp
from routes.vendors import vendors_bp
from routes.vessels import vessels_bp
from routes.invoices import invoices_bp

app.register_blueprint(items_bp, url_prefix='/items')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(employees_bp, url_prefix='/employees')
app.register_blueprint(timebooks_bp, url_prefix='/timebooks')
app.register_blueprint(control_panel_bp, url_prefix='/control-panel')
app.register_blueprint(contacts_bp, url_prefix='/contacts')
app.register_blueprint(customers_bp, url_prefix='/customers')
app.register_blueprint(jobs_bp, url_prefix='/jobs')
app.register_blueprint(purchase_orders_bp, url_prefix='/purchase_orders')
app.register_blueprint(vendors_bp, url_prefix='/vendors')
app.register_blueprint(vessels_bp, url_prefix='/vessels')
app.register_blueprint(invoices_bp, url_prefix='/invoices')

with app.app_context():
    db.create_all()

    # Attach models to app for easy access
    from models import User, Role, Contact, Customer, Employee, Item, Job, PurchaseOrder, Timebook, Vendor, Vessel
    app.Contact = Contact
    app.Customer = Customer
    app.Employee = Employee
    app.Item = Item
    app.Job = Job
    app.PurchaseOrder = PurchaseOrder
    app.Timebook = Timebook
    app.Vendor = Vendor
    app.Vessel = Vessel
    app.User = User
    app.Role = Role
    app.db = db

        # === ENSURE ADMIN HAS FULL PERMISSIONS INCLUDING VESSELS ===
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        # Load current permissions or create default
        try:
            perms = json.loads(admin_user.permissions) if admin_user.permissions else {}
        except:
            perms = {}
        
        # Make sure admin has ALL permissions including vessels
        full_perms = {
            "employees": "true",
            "timebooks": "true",
            "contacts": "true",
            "customers": "true",
            "items": "true",
            "jobs": "true",
            "purchase_orders": "true",
            "vendors": "true",
            "vessels": "true"  # THIS UNLOCKS VESSELS + ADD VESSEL BUTTON
        }
        perms.update(full_perms)
        admin_user.permissions = json.dumps(perms)
        db.session.commit()

    # Your existing user migration and creation code stays here
    # ... (keep all your existing code in this block)

# Custom index route
@app.route('/')
def index():
    from routes.auth import login_required
    return login_required(lambda: render_template('index.html', counts={
        'contacts': current_app.Contact.query.count(),
        'customers': current_app.Customer.query.count(),
        'employees': current_app.Employee.query.count(),
        'items': current_app.Item.query.count(),
        'jobs': current_app.Job.query.count(),
        'purchase_orders': current_app.PurchaseOrder.query.count(),
        'timebooks': current_app.Timebook.query.count(),
        'vendors': current_app.Vendor.query.count(),
        'vessels': current_app.Vessel.query.count(),
    }, current_date=datetime.now().strftime('%B %d, %Y %I:%M %p CST')))()

if __name__ == '__main__':
    app.run(debug=True)
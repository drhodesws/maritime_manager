from flask import Flask, render_template, request, redirect, url_for, session, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  # Import datetime for current_date
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change to a secure random value
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maritime.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db = SQLAlchemy(app)

# Define models within app context
with app.app_context():
    class Contact(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
    app.Contact = Contact

    class Customer(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
    app.Customer = Customer

    class Employee(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        full_name = db.Column(db.String(100), nullable=False)
        date_of_birth = db.Column(db.Date)
        contact_info = db.Column(db.String(200))
        address = db.Column(db.String(300))
        hire_date = db.Column(db.Date)
        role_position = db.Column(db.String(100))
        payrate_rt = db.Column(db.Float)
        payrate_ot = db.Column(db.Float)
        stcw_certification = db.Column(db.String(200))
        twic_card = db.Column(db.String(200))
        merchant_mariner_credential_mmc = db.Column(db.String(200))
        electro_technical_officer_eto_certification = db.Column(db.String(200))
        osha_safety_certifications = db.Column(db.String(200))
        first_aid_cpr_aed = db.Column(db.String(200))
        huet_bosiet = db.Column(db.String(200))
        gmdss_operator = db.Column(db.String(200))
        vessel_tonnage_rating = db.Column(db.String(100))
        domestic_international_endorsement = db.Column(db.String(100))
        able_seafarer_deck_engine_ab_rating = db.Column(db.String(200))
        radar_arpa_endorsement = db.Column(db.String(200))
        ecdis_certification = db.Column(db.String(200))
        power_tools_proficiency = db.Column(db.String(200))
        multi_meter_usage = db.Column(db.String(200))
        nvrip_camera_systems = db.Column(db.String(200))
        marine_electronics_expertise = db.Column(db.String(200))
        uhf_vhf_radio_handling = db.Column(db.String(200))
        years_of_experience = db.Column(db.Integer)
        training_completion_log = db.Column(db.Text)
        performance_reviews = db.Column(db.Text)
        upgrade_eligibility_flags = db.Column(db.String(200))
        promotion_history = db.Column(db.Text)
        expiration_alerts = db.Column(db.Text)

        def __getattr__(self, name):
            if name in self.__dict__:
                value = self.__dict__[name]
                return value if value is not None else ''
            raise AttributeError
    app.Employee = Employee

    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
    app.Item = Item

    class Job(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
    app.Job = Job

    class PurchaseOrder(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
    app.PurchaseOrder = PurchaseOrder

    class Timebook(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        employee = db.Column(db.String(100), nullable=False)
        description = db.Column(db.String(200))
        time_date = db.Column(db.Date)
        start_time = db.Column(db.String(5))
        stop_time = db.Column(db.String(5))
        job = db.Column(db.String(100))
        job_number = db.Column(db.String(10))
        mileage = db.Column(db.Integer)
        location = db.Column(db.String(100))

        def calculate_hours(self):
            if self.start_time == "-" or self.stop_time == "-":
                return 0.0
            try:
                start = datetime.strptime(self.start_time, '%H:%M')
                stop = datetime.strptime(self.stop_time, '%H:%M')
                time_diff = stop - start
                return time_diff.total_seconds() / 3600
            except ValueError:
                return 0.0
    app.Timebook = Timebook

    class Vendor(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
    app.Vendor = Vendor

    class Vessel(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
    app.Vessel = Vessel

    app.db = db  # Assign db to app attribute

# Hardcoded users (username: password, role)
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'user1': {'password': 'user123', 'role': 'user'}
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Before request to enforce login on all pages
@app.before_request
def require_login():
    if request.endpoint and request.endpoint != 'login' and request.endpoint != 'static' and 'username' not in session:
        return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username]['password'] == password:
            session['username'] = username
            session['role'] = USERS[username]['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# Import and register blueprints
with app.app_context():
    from routes.employees import employees_bp
    from routes.timebooks import timebooks_bp
    app.register_blueprint(employees_bp)
    app.register_blueprint(timebooks_bp)

# Dashboard route
@app.route('/')
@login_required
def index():
    counts = {
        'contacts': app.Contact.query.count(),
        'customers': app.Customer.query.count(),
        'employees': app.Employee.query.count(),
        'items': app.Item.query.count(),
        'jobs': app.Job.query.count(),
        'purchase_orders': app.PurchaseOrder.query.count(),
        'timebooks': app.Timebook.query.count(),
        'vendors': app.Vendor.query.count(),
        'vessels': app.Vessel.query.count(),
    }
    return render_template('index.html', counts=counts, current_date=datetime.now().strftime('%B %d, %Y %I:%M %p CST'))

if __name__ == '__main__':
    app.run(debug=True)
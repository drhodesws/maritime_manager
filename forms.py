# forms.py — FINAL & 100% WORKING — ALL FORMS INCLUDING NEW PURCHASE ORDER
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField,
    DecimalField, SelectField, BooleanField, DateField, TimeField,
    FloatField, IntegerField
)
from wtforms.validators import DataRequired, Email, EqualTo, Optional, NumberRange, Length
from models import Vessel, Customer, Vendor, Job, Role

# === LOGIN ===
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# === VESSEL ===
class VesselForm(FlaskForm):
    vessel_name = StringField('Vessel Name', validators=[DataRequired()])
    imo_number = StringField('IMO Number')
    build_year = IntegerField('Build Year')
    vessel_type = StringField('Vessel Type')
    gross_tonnage_gt = FloatField('Gross Tonnage (GT)')
    flag_state = StringField('Flag State')
    uscg_documentation = StringField('USCG Documentation #')
    radar_system = StringField('Radar System')
    route_type = StringField('Route Type')
    submit = SubmitField('Save Vessel')

# === JOB ===
class JobForm(FlaskForm):
    scheduled_date = DateField('Scheduled Work Date', format='%Y-%m-%d', validators=[DataRequired()])
    requested_service = TextAreaField('Requested  Requested Service / Problems Reported', validators=[DataRequired()])
    vessel_id = SelectField('Vessel', coerce=int, validators=[DataRequired()])
    customer_id = SelectField('Customer (Optional)', coerce=int)
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Save Job')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vessel_id.choices = [(0, '-- Select Vessel --')] + [
            (v.id, v.vessel_name) for v in Vessel.query.order_by(Vessel.vessel_name).all()
        ]
        self.customer_id.choices = [(0, '-- No Customer --')] + [
            (c.id, c.name) for c in Customer.query.order_by(Customer.name).all()
        ]

# === USER CREATION (used in employees.py) ===
class UserCreationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create User')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role.choices = [(r.id, r.name) for r in Role.query.order_by(Role.name).all()]

# === EMPLOYEE ===
class EmployeeForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    contact_info = TextAreaField('Contact Info')
    address = TextAreaField('Address')
    hire_date = DateField('Hire Date', format='%Y-%m-%d', validators=[Optional()])
    role_position = StringField('Role/Position')
    payrate_rt = DecimalField('Pay Rate (Regular)', places=2, validators=[Optional()])
    payrate_ot = DecimalField('Pay Rate (Overtime)', places=2, validators=[Optional()])
    stcw_certification = StringField('STCW Certification')
    twic_card = StringField('TWIC Card')
    merchant_mariner_credential_mmc = StringField('MMC')
    years_of_experience = StringField('Years of Experience')
    submit = SubmitField('Save Employee')

# === ITEM ===
class ItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    unit_price = DecimalField('Unit Price', places=2, validators=[DataRequired()])
    submit = SubmitField('Save Item')

# === VENDOR ===
class VendorForm(FlaskForm):
    name = StringField('Vendor Name', validators=[DataRequired()])
    contact_info = TextAreaField('Contact Info')
    address = TextAreaField('Address')
    phone = StringField('Phone')
    submit = SubmitField('Save Vendor')

# === CUSTOMER ===
class CustomerForm(FlaskForm):
    name = StringField('Customer Name', validators=[DataRequired()])
    contact_info = TextAreaField('Contact Info')
    address = TextAreaField('Address')
    phone = StringField('Phone')
    submit = SubmitField('Save Customer')

# === PURCHASE ORDER — NEW & PERFECTLY MATCHES YOUR FORM ===
class PurchaseOrderForm(FlaskForm):
    vendor_id = SelectField('Vendor', coerce=int, validators=[DataRequired()])
    job_id = SelectField('Job (Optional)', coerce=int, validators=[Optional()])
    customer_id = SelectField('Customer / Stock', coerce=int, validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    item_description = TextAreaField('Item Description', validators=[DataRequired()])
    notes = TextAreaField('Notes / Special Instructions', validators=[Optional()])
    submit = SubmitField('Create Purchase Order')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Vendors
        self.vendor_id.choices = [(0, '-- Select Vendor --')] + [
            (v.id, v.name) for v in Vendor.query.order_by(Vendor.name).all()
        ]
        # Jobs
        self.job_id.choices = [(0, '-- No Job --')] + [
            (j.id, f"{j.job_number} - {j.vessel.vessel_name if j.vessel else 'No Vessel'}")
            for j in Job.query.order_by(Job.job_number.desc()).all()
        ]
        # Customers
        self.customer_id.choices = [(0, 'Stock')] + [
            (c.id, c.name) for c in Customer.query.order_by(Customer.name).all()
        ]

# === TIMEBOOK ===
class TimebookForm(FlaskForm):
    employee = StringField('Employee', validators=[DataRequired()])
    description = TextAreaField('Description')
    time_date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    stop_time = TimeField('Stop Time', format='%H:%M', validators=[DataRequired()])
    job_number = StringField('Job #')
    mileage = FloatField('Mileage', validators=[Optional()])
    location = StringField('Location')
    billable = SelectField('Billable', choices=[('Yes', 'Yes'), ('No', 'No')], validators=[DataRequired()])
    pay_rate_rt = DecimalField('Pay Rate RT', places=2, validators=[Optional()])
    pay_rate_ot = DecimalField('Pay Rate OT', places=2, validators=[Optional()])
    submit = SubmitField('Submit')
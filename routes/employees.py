# routes/employees.py — FINAL & FULLY WORKING
from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from routes.auth import login_required, admin_required
from forms import EmployeeForm, UserCreationForm
from models import db, Employee, User, Role, Vessel, Timebook, Job
from datetime import datetime, timedelta
import random
import json
from config.permissions import PERMISSION_PAGES

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

@employees_bp.route('', methods=['GET', 'POST'])
@login_required
def list_employees():
    field_options = [
        {'value': 'full_name', 'label': 'Full Name'},
        {'value': 'date_of_birth', 'label': 'Date of Birth'},
        {'value': 'contact_info', 'label': 'Contact Info'},
        {'value': 'address', 'label': 'Address'},
        {'value': 'hire_date', 'label': 'Hire Date'},
        {'value': 'role_position', 'label': 'Role/Position'},
        {'value': 'payrate_rt', 'label': 'Pay Rate RT'},
        {'value': 'payrate_ot', 'label': 'Pay Rate OT'},
        {'value': 'stcw_certification', 'label': 'STCW Certification'},
        {'value': 'twic_card', 'label': 'TWIC Card'},
        {'value': 'merchant_mariner_credential_mmc', 'label': 'MMC'},
        {'value': 'years_of_experience', 'label': 'Years of Experience'},
    ]
    
    if request.method == 'POST':
        selected_fields = request.form.getlist('columns')
        return redirect(url_for('employees.list_employees', columns=selected_fields))
    else:
        selected_fields = request.args.getlist('columns') or ['full_name', 'role_position', 'hire_date', 'years_of_experience']
    
    employees = Employee.query.all()
    return render_template('employee_list.html', employees=employees, selected_fields=selected_fields, field_options=field_options)

@employees_bp.route('/employees', methods=['GET'])
@login_required
def employees_page():
    employee_count = current_app.Employee.query.count()
    return render_template('employees.html', employee_count=employee_count)

@employees_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_employee():
    form = EmployeeForm()
    user_form = UserCreationForm()
    roles = Role.query.all()

    if request.method == 'POST':
        if 'create_user' in request.form and user_form.validate_on_submit():
            employee = Employee(
                full_name=form.full_name.data,
                date_of_birth=form.date_of_birth.data,
                contact_info=form.contact_info.data,
                address=form.address.data,
                hire_date=form.hire_date.data,
                role_position=form.role_position.data,
                payrate_rt=form.payrate_rt.data,
                payrate_ot=form.payrate_ot.data,
                stcw_certification=form.stcw_certification.data,
                twic_card=form.twic_card.data,
                merchant_mariner_credential_mmc=form.merchant_mariner_credential_mmc.data,
                years_of_experience=form.years_of_experience.data,
            )
            db.session.add(employee)
            db.session.flush()

            role_id = user_form.role.data
            role = Role.query.get(role_id)
            permissions = {}
            if role and role.permissions:
                detailed = json.loads(role.permissions)
                for page, actions in detailed.items():
                    permissions[page] = 'true' if any(v == 'true' for v in actions.values()) else 'false'
            else:
                for page in PERMISSION_PAGES.keys():
                    permissions[page] = 'false'

            user = User(
                username=user_form.username.data,
                password=user_form.password.data,
                role='user',
                employee_full_name=employee.full_name,
                role_id=role_id,
                permissions=json.dumps(permissions)
            )
            user.set_password(user_form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Employee and user created successfully!', 'success')
            return redirect(url_for('employees.list_employees'))

        elif form.validate_on_submit():
            employee = Employee(
                full_name=form.full_name.data,
                date_of_birth=form.date_of_birth.data,
                contact_info=form.contact_info.data,
                address=form.address.data,
                hire_date=form.hire_date.data,
                role_position=form.role_position.data,
                payrate_rt=form.payrate_rt.data,
                payrate_ot=form.payrate_ot.data,
                stcw_certification=form.stcw_certification.data,
                twic_card=form.twic_card.data,
                merchant_mariner_credential_mmc=form.merchant_mariner_credential_mmc.data,
                years_of_experience=form.years_of_experience.data,
            )
            db.session.add(employee)
            db.session.commit()
            flash('Employee created successfully!', 'success')
            return redirect(url_for('employees.list_employees'))

    return render_template('employee_form.html', form=form, user_form=user_form, roles=roles, permission_pages=PERMISSION_PAGES, action='Create')

@employees_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_employee(id):
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)
    
    if form.validate_on_submit():
        employee.full_name = form.full_name.data
        employee.date_of_birth = form.date_of_birth.data
        employee.contact_info = form.contact_info.data
        employee.address = form.address.data
        employee.hire_date = form.hire_date.data
        employee.role_position = form.role_position.data
        employee.payrate_rt = form.payrate_rt.data
        employee.payrate_ot = form.payrate_ot.data
        employee.stcw_certification = form.stcw_certification.data
        employee.twic_card = form.twic_card.data
        employee.merchant_mariner_credential_mmc = form.merchant_mariner_credential_mmc.data
        employee.years_of_experience = form.years_of_experience.data
        db.session.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('employees.list_employees'))
    
    return render_template('employee_form.html', form=form, action='Update')

@employees_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!', 'success')
    return redirect(url_for('employees.list_employees'))

@employees_bp.route('/columns', methods=['GET', 'POST'])
@login_required
def select_columns():
    field_options = [
        {'value': 'full_name', 'label': 'Full Name'},
        {'value': 'date_of_birth', 'label': 'Date of Birth'},
        {'value': 'contact_info', 'label': 'Contact Info'},
        {'value': 'address', 'label': 'Address'},
        {'value': 'hire_date', 'label': 'Hire Date'},
        {'value': 'role_position', 'label': 'Role/Position'},
        {'value': 'payrate_rt', 'label': 'Pay Rate RT'},
        {'value': 'payrate_ot', 'label': 'Pay Rate OT'},
        {'value': 'stcw_certification', 'label': 'STCW Certification'},
        {'value': 'twic_card', 'label': 'TWIC Card'},
        {'value': 'merchant_mariner_credential_mmc', 'label': 'MMC'},
        {'value': 'years_of_experience', 'label': 'Years of Experience'},
    ]
    
    if request.method == 'POST':
        selected_fields = request.form.getlist('columns')
        return redirect(url_for('employees.list_employees', columns=selected_fields))
    else:
        selected_fields = request.args.getlist('columns') or ['full_name', 'role_position', 'hire_date', 'years_of_experience']
    
    return render_template('employee_columns.html', field_options=field_options, selected_fields=selected_fields)

@employees_bp.route('/load-sample-data', methods=['GET', 'POST'])
@login_required
@admin_required
def load_sample_data():
    # === FULL WIPE & RESET ===
    db.session.query(Timebook).delete()
    db.session.query(Job).delete()
    db.session.query(Employee).delete()
    db.session.query(Vessel).delete()
    db.session.query(Role).delete()
    db.session.commit()

    # === ROLES ===
    admin_role = Role(name="Admin", permissions=json.dumps({
        page: {'list': 'true', 'create': 'true', 'edit': 'true', 'delete': 'true'}
        for page in PERMISSION_PAGES.keys()
    }))
    user_role = Role(name="User", permissions=json.dumps({
        "employees": {"list": "true", "create": "false", "edit": "false", "delete": "false"},
        "timebooks": {"list": "true", "create": "true", "edit": "true", "delete": "false"},
        "jobs": {"list": "true", "create": "false", "edit": "false", "delete": "false"},
        **{page: {"list": "false", "create": "false", "edit": "false", "delete": "false"}
           for page in PERMISSION_PAGES.keys() if page not in ["employees", "timebooks", "jobs"]}
    }))
    db.session.add_all([admin_role, user_role])
    db.session.commit()

    # === VESSELS ===
    vessel1 = Vessel(vessel_name="M/V Sea Hawk", imo_number="1234567")
    vessel2 = Vessel(vessel_name="M/V Ocean Star", imo_number="9876543")
    db.session.add_all([vessel1, vessel2])
    db.session.commit()

    # === EMPLOYEES ===
    emp1 = Employee(full_name="John Davis", role_position="Captain", payrate_rt=85.00)
    emp2 = Employee(full_name="Mike Torres", role_position="Engineer", payrate_rt=75.00)
    db.session.add_all([emp1, emp2])
    db.session.commit()

    # === JOBS — Force fresh numbers by overriding job_number ===
    job1 = Job(
        job_number="11250001",  # Force it — safe because we wiped the table
        scheduled_date=datetime(2025, 11, 18),
        requested_service="Annual engine overhaul and dry dock prep",
        vessel_id=vessel1.id,
        location="Port of Galveston",
        customer_id=None
    )
    job2 = Job(
        job_number="11250002",  # Force next number
        scheduled_date=datetime(2025, 11, 20),
        requested_service="Electrical system upgrade and generator service",
        vessel_id=vessel2.id,
        location="Port of Houston",
        customer_id=None
    )
    db.session.add_all([job1, job2])
    db.session.commit()

    # === TIMEBOOK — 2 weeks of data (Nov 10–23, 2025) ===
    start_date = datetime(2025, 11, 10)
    for day_offset in range(14):
        current_date = start_date + timedelta(days=day_offset)
        if current_date.weekday() >= 5:  # Skip weekends
            continue

        for emp, job in [(emp1, job1), (emp2, job2), (emp1, job2), (emp2, job1)]:
            hours = random.uniform(8.0, 12.0)
            entry = Timebook(
                employee=emp.full_name,
                description=f"Work on {job.requested_service[:50]}...",
                time_date=current_date.date(),
                start_time=datetime.strptime("07:00", "%H:%M").time(),
                stop_time=(datetime.combine(current_date, datetime.strptime("07:00", "%H:%M").time()) + timedelta(hours=hours)).time(),
                job_number=job.job_number,
                location=job.location,
                billable="Yes",
                pay_rate_rt=emp.payrate_rt,
                pay_rate_ot=emp.payrate_rt * 1.5
            )
            db.session.add(entry)

    db.session.commit()
    flash('Sample data loaded successfully! (2 vessels, 2 employees, 2 jobs, 2 weeks of time)', 'success')
    return redirect(url_for('employees.employees_page'))
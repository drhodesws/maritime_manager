from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
from models import Timebook, Employee, User  # Assuming User model exists for permissions
from datetime import datetime, timedelta, time
from routes.auth import login_required
from forms import TimebookForm

timebooks_bp = Blueprint('timebooks', __name__, url_prefix='/timebooks')

# Modular function to handle timebook form processing (reusable for create/update)
def process_timebook_form(db, Timebook, form, action='create'):
    if form.validate_on_submit():
        # Convert string times to time objects if necessary
        start_time = form.start_time.data
        stop_time = form.stop_time.data
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%H:%M').time()
        if isinstance(stop_time, str):
            stop_time = datetime.strptime(stop_time, '%H:%M').time()

        timebook_data = {
            'employee': form.employee.data,
            'description': form.description.data,
            'time_date': form.time_date.data,
            'start_time': start_time,
            'stop_time': stop_time,
            'job_number': form.job_number.data,
            'mileage': form.mileage.data,
            'location': form.location.data,
            'billable': form.billable.data,
            'pay_rate_rt': form.pay_rate_rt.data,
            'pay_rate_ot': form.pay_rate_ot.data,
            'paid': False
        }
        if action == 'update':
            timebook = form.timebook  # Assume timebook is passed via form for updates
            for key, value in timebook_data.items():
                setattr(timebook, key, value)
            db.session.commit()
            flash('Time entry updated successfully!', 'success')
        else:  # create
            timebook = Timebook(**timebook_data)
            db.session.add(timebook)
            db.session.commit()
            flash('Time entry created successfully!', 'success')
        return redirect(url_for('timebooks.timebook_week', employee=form.employee.data, start_date=request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))))
    else:
        print(f"Validation errors: {form.errors}")
        flash('Invalid form data. Please check your inputs and correct the errors below.', 'error')
    return None

def populate_sample_data(db, Timebook, datetime, timedelta):
    pass  # Placeholder; sample data is loaded via Employees

@timebooks_bp.route('', methods=['GET', 'POST'])
@login_required
def list_timebooks():
    db = current_app.db
    Timebook = current_app.Timebook
    Employee = current_app.Employee

    # Get all employees for the dropdown
    employees = Employee.query.all()
    selected_employee = request.form.get('employee') or request.args.get('employee')

    # Determine the current user's employee context
    current_employee = session.get('employee_full_name')
    if not current_employee and session['role'] in ['user', 'NP']:
        current_employee = next((e.full_name for e in employees if e.full_name == session['username']), None)
        if not current_employee and session['role'] == 'NP':
            current_employee = session.get('employee_full_name') or next((e.full_name for e in employees), None)

    # Fetch Timebooks, filtered by selected employee or current user if no selection
    if selected_employee:
        timebooks = Timebook.query.filter_by(employee=selected_employee).all()
    elif current_employee and session['role'] != 'admin':
        timebooks = Timebook.query.filter_by(employee=current_employee).all()
    else:
        timebooks = Timebook.query.all()

    # Calculate hours and handle read-only status
    for timebook in timebooks:
        timebook.hours = getattr(timebook, 'calculate_hours', lambda: 0)()  # Safe call, defaults to 0 if method missing
        if session.get('role') == 'NP' and not timebook.pay_rate_rt and not timebook.pay_rate_ot:
            timebook.pay_rate_rt = 0.0
            timebook.pay_rate_ot = 0.0

    # Weekly split
    week1_end = datetime(2025, 11, 15).date()
    timebooks_week1 = [t for t in timebooks if t.time_date <= week1_end]
    timebooks_week2 = [t for t in timebooks if t.time_date > week1_end]

    view = request.form.get('view') or request.args.get('view') or 'classic'
    return render_template('timebook_list.html', timebooks=timebooks, timebooks_week1=timebooks_week1, timebooks_week2=timebooks_week2, view=view, current_date=datetime.now(), employees=employees, selected_employee=selected_employee)

@timebooks_bp.route('/timebooks', methods=['GET'])
@login_required
def timebooks_page():
    db = current_app.db
    Employee = current_app.Employee
    employees = Employee.query.all()  # Fetch all employees
    current_employee = session.get('employee_full_name')
    if not current_employee and session['role'] in ['user', 'NP']:
        current_employee = next((e.full_name for e in employees if e.full_name == session['username']), None)
        if not current_employee and session['role'] == 'NP':
            current_employee = session.get('employee_full_name') or next((e.full_name for e in employees), None)

    if current_employee and session['role'] != 'admin':
        return redirect(url_for('timebooks.timebook_week', employee=current_employee))
    return render_template('timebooks.html', employees=employees)

@timebooks_bp.route('/week', methods=['GET', 'POST'])
@login_required
def timebook_week():
    db = current_app.db
    Timebook = current_app.Timebook
    Employee = current_app.Employee
    User = current_app.User  # Assuming User model exists

    # Get all employees and users for the dropdown
    employees = Employee.query.all()
    users = User.query.all()  # Fetch all users for the control panel

    # Determine the current user's employee context or admin selection
    current_employee = session.get('employee_full_name')
    if not current_employee and session['role'] in ['user', 'NP']:
        current_employee = next((e.full_name for e in employees if e.full_name == session['username']), None)
        if not current_employee and session['role'] == 'NP':
            current_employee = session.get('employee_full_name') or next((e.full_name for e in employees), None)

    # Set selected_employee based on role and input
    if session['role'] == 'admin':
        selected_employee = request.form.get('employee') or request.args.get('employee') or None
    else:
        selected_employee = request.form.get('employee') or current_employee  # Only allow form override for non-admins

    if not selected_employee and session['role'] != 'admin':
        flash('You must be associated with an employee to view the week.', 'error')
        return redirect(url_for('timebooks.timebooks_page'))

    # Get current week dates based on start_date parameter
    start_date_str = request.args.get('start_date')
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            today = datetime.now().date()
            start_date = today - timedelta(days=today.weekday())  # Default to current week on invalid date
    else:
        today = datetime.now().date()
        start_date = today - timedelta(days=today.weekday())  # Monday of current week
    week_dates = [start_date + timedelta(days=i) for i in range(7)]  # Monday to Sunday

    # Calculate week options for dropdown (current week and previous weeks)
    current_date = datetime.now()
    week_options = []
    for i in range(4):  # Current week (i=0) and 3 previous weeks
        week_start = current_date - timedelta(days=(current_date.weekday() + 7 * i))
        label = 'Current Week' if i == 0 else f'Week -{i}'
        week_options.append({
            'start_date': week_start.strftime('%Y-%m-%d'),
            'label': f"{label} ({week_start.strftime('%B %d, %Y')})"
        })
    print(f"Week options: {week_options}")  # Debug print to verify data

    # Fetch time entries for the current week and selected employee
    if session['role'] == 'admin' and not selected_employee:
        time_entries = Timebook.query.filter(Timebook.time_date.in_(week_dates)).all()  # All employees for admin
    else:
        time_entries = Timebook.query.filter(
            Timebook.time_date.in_(week_dates),
            Timebook.employee == (selected_employee or current_employee)  # Use current_employee as fallback for non-admins
        ).all() if selected_employee or current_employee else []

    # Group entries by date, ensuring all dates are included even if empty
    entries_by_date = {date: [t for t in time_entries if t.time_date == date] for date in week_dates}

    # Instantiate form for the template
    form = TimebookForm(employees=employees)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            if form.validate_on_submit():
                selected_date = request.form.get('selected_date')
                if selected_date:
                    timebook = Timebook(
                        employee=form.employee.data,
                        description=form.description.data,
                        time_date=datetime.strptime(selected_date, '%Y-%m-%d').date(),
                        start_time=form.start_time.data,
                        stop_time=form.stop_time.data,
                        job_number=form.job_number.data,
                        mileage=form.mileage.data,
                        location=form.location.data,
                        billable=form.billable.data,
                        pay_rate_rt=form.pay_rate_rt.data,
                        pay_rate_ot=form.pay_rate_ot.data,
                        paid=False
                    )
                    db.session.add(timebook)
                    db.session.commit()
                    flash('Time entry added successfully!', 'success')
        elif action == 'edit':
            entry_id = request.form.get('entry_id')
            if entry_id:
                timebook = Timebook.query.get_or_404(entry_id)
                if (session['role'] != 'admin' and session.get('employee_full_name') != timebook.employee) or timebook.paid:
                    flash('You cannot edit this time entry.', 'error')
                else:
                    form.timebook = timebook
                    result = process_timebook_form(db, Timebook, form, action='update')
                    if result:
                        return result
        else:
            print(f"Validation errors: {form.errors}")
            flash('Invalid form data or action. Please check your inputs.', 'error')

    # Pre-select employee for non-admins or use selected employee for admins
    if current_employee and session['role'] != 'admin':
        form.employee.data = current_employee
    elif selected_employee and session['role'] == 'admin':
        form.employee.data = selected_employee
    elif not form.employee.data and employees and session['role'] != 'admin':
        form.employee.data = employees[0].full_name  # Default for non-admins

    # Get or set default colors from session
    header_color = session.get('header_color', '#1da1f2')
    button_color = session.get('button_color', '#1da1f2')
    background_color = session.get('background_color', '#f0f0f0')

    # Get selected user and permissions for control panel
    selected_user_id = request.form.get('user_id')
    selected_user = User.query.get(selected_user_id) if selected_user_id else None
    selected_permissions = session.get('permissions', {}).get(selected_user_id, {}) if selected_user_id else {}

    if request.method == 'POST' and 'save' in request.form and session['role'] == 'admin':
        permissions = {
            'employees': 'true' if 'employees' in request.form else 'false',
            'timebooks': 'true' if 'timebooks' in request.form else 'false',
            'contacts': 'true' if 'contacts' in request.form else 'false',
            'customers': 'true' if 'customers' in request.form else 'false',
            'items': 'true' if 'items' in request.form else 'false',
            'jobs': 'true' if 'jobs' in request.form else 'false',
            'purchase_orders': 'true' if 'purchase_orders' in request.form else 'false',
            'vendors': 'true' if 'vendors' in request.form else 'false',
            'vessels': 'true' if 'vessels' in request.form else 'false'
        }
        if 'permissions' not in session:
            session['permissions'] = {}
        session['permissions'][selected_user_id] = permissions
        db.session.commit()  # Assuming session changes are committed
        flash('Permissions updated successfully!', 'success')
        return redirect(url_for('timebooks.timebook_week'))

    return render_template('timebook_week.html', week_dates=week_dates, entries_by_date=entries_by_date, current_employee=current_employee, form=form, employees=employees, selected_employee=selected_employee, current_date=current_date, week_options=week_options, start_date=start_date, header_color=header_color, button_color=button_color, background_color=background_color, users=users, selected_user=selected_user, selected_permissions=selected_permissions)

@timebooks_bp.route('/color_panel', methods=['GET', 'POST'])
@login_required
def color_panel():
    if request.method == 'POST':
        session['header_color'] = request.form.get('header_color', '#1da1f2')
        session['button_color'] = request.form.get('button_color', '#1da1f2')
        session['background_color'] = request.form.get('background_color', '#f0f0f0')
        flash('Colors updated successfully!', 'success')
        return redirect(url_for('timebooks.timebook_week'))
    
    # Default colors from session
    header_color = session.get('header_color', '#1da1f2')
    button_color = session.get('button_color', '#1da1f2')
    background_color = session.get('background_color', '#f0f0f0')
    
    return render_template('color_panel.html', header_color=header_color, button_color=button_color, background_color=background_color)

@timebooks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_timebook():
    db = current_app.db
    Timebook = current_app.Timebook
    Employee = current_app.Employee
    employees = Employee.query.all()
    form = TimebookForm(employees=employees)

    if request.method == 'POST' and form.validate_on_submit():
        timebook = Timebook(
            employee=form.employee.data,
            description=form.description.data,
            time_date=form.time_date.data,
            start_time=form.start_time.data,
            stop_time=form.stop_time.data,
            job_number=form.job_number.data,
            mileage=form.mileage.data,
            location=form.location.data,
            billable=form.billable.data,
            pay_rate_rt=form.pay_rate_rt.data,
            pay_rate_ot=form.pay_rate_ot.data,
            paid=False
        )
        db.session.add(timebook)
        db.session.commit()
        flash('Time entry created successfully!', 'success')
        return redirect(url_for('timebooks.timebook_week', employee=form.employee.data))
    return render_template('timebook_form.html', form=form)

@timebooks_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_timebook(id):
    # Preserve this route for future enhancements (e.g., images, job details)
    db = current_app.db
    Timebook = current_app.Timebook
    Employee = current_app.Employee
    employees = Employee.query.all()
    timebook = Timebook.query.get_or_404(id)

    # Check authorization
    current_employee = session.get('employee_full_name')
    if not current_employee and session['role'] in ['user', 'NP']:
        current_employee = next((e.full_name for e in employees if e.full_name == session['username']), None)
        if not current_employee and session['role'] == 'NP':
            current_employee = session.get('employee_full_name')
    if current_employee != timebook.employee and session['role'] != 'admin':
        flash('You can only edit your own time entries.', 'error')
        return redirect(url_for('timebooks.timebook_week', employee=current_employee))

    form = TimebookForm(employees=employees, obj=timebook)
    form.timebook = timebook

    if request.method == 'POST':
        result = process_timebook_form(db, Timebook, form, action='update')
        if result:
            return result
        return render_template('edit_timebook.html', form=form, timebook=timebook)

    # Convert string times from database to time objects for TimeField
    if isinstance(timebook.start_time, str):
        form.start_time.data = datetime.strptime(timebook.start_time, '%H:%M').time()
    if isinstance(timebook.stop_time, str):
        form.stop_time.data = datetime.strptime(timebook.stop_time, '%H:%M').time()

    return render_template('edit_timebook.html', form=form, timebook=timebook)

@timebooks_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_timebook(id):
    db = current_app.db
    Timebook = current_app.Timebook
    timebook = Timebook.query.get_or_404(id)

    # Check if the entry is paid (read-only)
    if timebook.paid:
        flash('This time entry is paid and can only be viewed.', 'error')
        return redirect(url_for('timebooks.list_timebooks'))

    # Determine current employee for authorization
    current_employee = session.get('employee_full_name')
    if not current_employee and session['role'] in ['user', 'NP']:
        current_employee = next((e.full_name for e in Employee.query.all() if e.full_name == session['username']), None)
        if not current_employee and session['role'] == 'NP':
            current_employee = session.get('employee_full_name')
    if current_employee != timebook.employee and session['role'] != 'admin':
        flash('You can only edit your own time entries.', 'error')
        return redirect(url_for('timebooks.list_timebooks'))

    form = TimebookForm(employees=Employee.query.all())
    if request.method == 'POST':
        # Ensure employee is included from hidden field if disabled
        if session.get('employee_full_name') or session['role'] == 'user':
            form.employee.data = request.form.get('employee', timebook.employee)
        if form.validate_on_submit():
            timebook.employee = form.employee.data
            timebook.description = form.description.data
            timebook.time_date = form.time_date.data
            timebook.start_time = form.start_time.data
            timebook.stop_time = form.stop_time.data
            timebook.job_number = form.job_number.data
            timebook.mileage = form.mileage.data
            timebook.location = form.location.data
            timebook.billable = form.billable.data
            timebook.pay_rate_rt = form.pay_rate_rt.data
            timebook.pay_rate_ot = form.pay_rate_ot.data
            db.session.commit()
            flash('Time entry updated successfully!', 'success')
            return redirect(url_for('timebooks.list_timebooks'))
        else:
            print(f"Validation errors: {form.errors}")
            flash('Invalid form data. Please check your inputs and correct the errors below.', 'error')

    # Pre-fill form with existing data
    form.process(obj=timebook)
    if timebook.employee and session['role'] != 'admin':
        form.employee.data = timebook.employee
    return render_template('timebook_form.html', form=form)

@timebooks_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_timebook(id):
    db = current_app.db
    Timebook = current_app.Timebook
    timebook = Timebook.query.get_or_404(id)

    # Check if the entry is paid (read-only)
    if timebook.paid:
        flash('This time entry is paid and cannot be deleted.', 'error')
        return redirect(url_for('timebooks.list_timebooks'))

    # Determine current employee for authorization
    current_employee = session.get('employee_full_name')
    if not current_employee and session['role'] in ['user', 'NP']:
        current_employee = next((e.full_name for e in Employee.query.all() if e.full_name == session['username']), None)
        if not current_employee and session['role'] == 'NP':
            current_employee = session.get('employee_full_name')
    if current_employee != timebook.employee and session['role'] != 'admin':
        flash('You can only delete your own time entries.', 'error')
        return redirect(url_for('timebooks.list_timebooks'))

    db.session.delete(timebook)
    db.session.commit()
    flash('Time entry deleted successfully!', 'success')
    return redirect(url_for('timebooks.list_timebooks'))
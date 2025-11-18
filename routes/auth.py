from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import json
from models import db, User, Role, Employee
from werkzeug.security import check_password_hash
from config.permissions import PERMISSION_PAGES  # ← Fixed import

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session.get('role') != 'admin':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session.clear()
            session['username'] = user.username
            session['role'] = user.role
            session['employee_full_name'] = user.employee_full_name
            
            try:
                session['permissions'] = json.loads(user.permissions) if user.permissions else {}
            except:
                session['permissions'] = {}
                
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    roles = Role.query.all()
    employees = Employee.query.order_by(Employee.full_name).all()

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role_id = request.form.get('role_id')
        employee_full_name = request.form.get('employee_full_name')
        is_np = 'is_np' in request.form

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return render_template('create_user.html', roles=roles, employees=employees)

        flat_perms = {}
        if role_id:
            role_obj = Role.query.get(role_id)
            if role_obj and role_obj.permissions:
                detailed = json.loads(role_obj.permissions)
                for page, actions in detailed.items():
                    flat_perms[page] = 'true' if any(v == 'true' for v in actions.values()) else 'false'
            else:
                for page in PERMISSION_PAGES.keys():
                    flat_perms[page] = 'false'
        else:
            for page in PERMISSION_PAGES.keys():
                flat_perms[page] = 'false'

        new_user = User(
            username=username,
            password=password,
            role='admin' if role_id and Role.query.get(role_id).name == 'Admin' else 'user',
            employee_full_name=None if is_np else employee_full_name,
            permissions=json.dumps(flat_perms),
            role_id=int(role_id) if role_id else None
        )
        db.session.add(new_user)
        db.session.commit()
        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('control_panel.control_panel'))

    return render_template('create_user.html', roles=roles, employees=employees)
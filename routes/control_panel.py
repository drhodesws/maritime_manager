from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, admin_required
from models import db, Role, User
import json
from routes.employees import PERMISSION_PAGES

control_panel_bp = Blueprint('control_panel', __name__, url_prefix='/control-panel')

# THIS IS THE MISSING ROUTE — CONTROL PANEL HOME PAGE
@control_panel_bp.route('/')
@login_required
@admin_required
def control_panel():
    return render_template('control_panel.html')

# Roles List
@control_panel_bp.route('/roles', methods=['GET'])
@control_panel_bp.route('/manage_roles', methods=['GET'])
@login_required
@admin_required
def roles_list():
    roles = Role.query.all()
    return render_template('roles_list.html', roles=roles)

# Role Create/Edit Form
@control_panel_bp.route('/roles/create', methods=['GET', 'POST'])
@control_panel_bp.route('/roles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def role_form(id=None):
    role = Role.query.get_or_404(id) if id else None
    
    if request.method == 'POST':
        name = request.form.get('name')
        
        detailed_perms = {}
        flat_perms = {}
        for page, actions in PERMISSION_PAGES.items():
            detailed_perms[page] = {}
            has_access = False
            for action in actions:
                checked = request.form.get(f'{page}_{action}') == 'on'
                detailed_perms[page][action] = 'true' if checked else 'false'
                if checked:
                    has_access = True
            flat_perms[page] = 'true' if has_access else 'false'
        
        permissions_json = json.dumps(detailed_perms)
        flat_permissions_json = json.dumps(flat_perms)
        
        if role:
            role.name = name
            role.permissions = permissions_json
            role_id = role.id
            flash('Role updated successfully!', 'success')
        else:
            new_role = Role(name=name, permissions=permissions_json)
            db.session.add(new_role)
            db.session.flush()
            role_id = new_role.id
            role = new_role
            flash('Role created successfully!', 'success')
        
        User.query.filter_by(role=name).update({"role_id": role_id, "permissions": flat_permissions_json})
        db.session.commit()
        return redirect(url_for('control_panel.roles_list'))

    checked = {}
    if role and role.permissions:
        try:
            perm_dict = json.loads(role.permissions)
            for page, actions in perm_dict.items():
                for action, value in actions.items():
                    checked[f'{page}_{action}'] = (value == 'true')
        except:
            pass

    return render_template('role_form.html', role=role, permission_pages=PERMISSION_PAGES, checked=checked)

# Delete Role
@control_panel_bp.route('/roles/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_role(id):
    role = Role.query.get_or_404(id)
    User.query.filter_by(role_id=id).update({"permissions": json.dumps({})})
    db.session.delete(role)
    db.session.commit()
    flash('Role deleted successfully!', 'success')
    return redirect(url_for('control_panel.roles_list'))

# Users List
@control_panel_bp.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.all()
    roles = Role.query.all()
    return render_template('users_list.html', users=users, roles=roles)

# Edit User
@control_panel_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    roles = Role.query.all()

    if request.method == 'POST':
        username = request.form['username']
        employee_full_name = request.form.get('employee_full_name') or None
        selected_role_id = request.form.get('role_id')

        if user.username == 'admin' and username != 'admin':
            flash('Cannot change the primary admin username!', 'danger')
            return redirect(url_for('control_panel.users_list'))

        user.username = username
        user.employee_full_name = employee_full_name
        user.role_id = int(selected_role_id) if selected_role_id else None

        if selected_role_id:
            selected_role = Role.query.get(selected_role_id)
            if selected_role and selected_role.permissions:
                detailed = json.loads(selected_role.permissions)
                flat = {}
                for page, actions in detailed.items():
                    flat[page] = 'true' if any(v == 'true' for v in actions.values()) else 'false'
                user.permissions = json.dumps(flat)
            else:
                user.permissions = json.dumps({})
        else:
            user.permissions = json.dumps({})

        db.session.commit()
        flash(f'User {username} updated successfully!', 'success')
        return redirect(url_for('control_panel.users_list'))

    return render_template('user_form.html', user=user, roles=roles)

# Delete User
@control_panel_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.username == 'admin':
        flash('Cannot delete the primary admin account!', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    return redirect(url_for('control_panel.users_list'))
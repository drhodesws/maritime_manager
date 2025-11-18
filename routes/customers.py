# routes/customers.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, admin_required
from models import db, Customer
from forms import CustomerForm

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

@customers_bp.route('/')
@login_required
def customers_page():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@customers_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            contact_info=form.contact_info.data,
            address=form.address.data,
            phone=form.phone.data
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer created!', 'success')
        return redirect(url_for('customers.customers_page'))
    return render_template('customer_form.html', form=form, action='Create')

@customers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.contact_info = form.contact_info.data
        customer.address = form.address.data
        customer.phone = form.phone.data
        db.session.commit()
        flash('Customer updated!', 'success')
        return redirect(url_for('customers.customers_page'))
    return render_template('customer_form.html', form=form, customer=customer, action='Edit')

@customers_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted!', 'success')
    return redirect(url_for('customers.customers_page'))
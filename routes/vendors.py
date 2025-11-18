# routes/vendors.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, admin_required
from models import db, Vendor
from forms import VendorForm

vendors_bp = Blueprint('vendors', __name__, url_prefix='/vendors')

@vendors_bp.route('/')
@login_required
def vendors_page():
    vendors = Vendor.query.all()
    return render_template('vendors.html', vendors=vendors)

@vendors_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_vendor():
    form = VendorForm()
    if form.validate_on_submit():
        vendor = Vendor(
            name=form.name.data,
            contact_info=form.contact_info.data,
            address=form.address.data,
            phone=form.phone.data
        )
        db.session.add(vendor)
        db.session.commit()
        flash('Vendor created!', 'success')
        return redirect(url_for('vendors.vendors_page'))
    return render_template('vendor_form.html', form=form, action='Create')

@vendors_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    form = VendorForm(obj=vendor)
    if form.validate_on_submit():
        vendor.name = form.name.data
        vendor.contact_info = form.contact_info.data
        vendor.address = form.address.data
        vendor.phone = form.phone.data
        db.session.commit()
        flash('Vendor updated!', 'success')
        return redirect(url_for('vendors.vendors_page'))
    return render_template('vendor_form.html', form=form, vendor=vendor, action='Edit')

@vendors_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    db.session.delete(vendor)
    db.session.commit()
    flash('Vendor deleted!', 'success')
    return redirect(url_for('vendors.vendors_page'))
# routes/purchase_orders.py — FINAL & 100% WORKING — NO MORE ERRORS
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from routes.auth import login_required
from models import db, PurchaseOrder, Vendor, Customer, Job, User
from forms import PurchaseOrderForm

purchase_orders_bp = Blueprint('purchase_orders', __name__, url_prefix='/purchase_orders')

@purchase_orders_bp.before_request
@login_required
def before_request():
    g.current_user = User.query.filter_by(username=session['username']).first()

@purchase_orders_bp.route('/')
@login_required
def purchase_orders_page():
    page = request.args.get('page', 1, type=int)
    per_page = 25
    pos = PurchaseOrder.query.order_by(PurchaseOrder.created_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    return render_template('purchase_orders.html', pos=pos)

@purchase_orders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_po():
    form = PurchaseOrderForm()

    # SAFE JSON DATA — this is the fix
    vendors = [{'id': v.id, 'name': v.name} for v in Vendor.query.order_by(Vendor.name).all()]
    jobs = [{
        'id': j.id,
        'job_number': j.job_number,
        'vessel_name': j.vessel.vessel_name if j.vessel else 'No Vessel'
    } for j in Job.query.order_by(Job.job_number.desc()).all()]

    if form.validate_on_submit():
        po = PurchaseOrder(
            vendor_id=request.form.get('vendor_id'),
            job_id=request.form.get('job_id') or None,
            customer_id=request.form.get('customer_id') or None,
            quantity=form.quantity.data,
            item_description=request.form.get('item_description'),
            notes=form.notes.data
        )
        db.session.add(po)
        db.session.commit()
        flash(f'PO {po.order_number} created!', 'success')
        return redirect(url_for('purchase_orders.purchase_orders_page'))

    return render_template(
        'po_form.html',
        form=form,
        action='Create',
        vendors=vendors,
        jobs=jobs
    )
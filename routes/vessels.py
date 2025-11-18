# routes/vessels.py — COMPLETE & WORKING
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, admin_required
from models import db, Vessel
from forms import VesselForm

vessels_bp = Blueprint('vessels', __name__, url_prefix='/vessels')

@vessels_bp.route('/')
@login_required
def vessels_page():
    vessels = Vessel.query.all()
    return render_template('vessel_list.html', vessels=vessels)

@vessels_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_vessel():
    form = VesselForm()
    if form.validate_on_submit():
        vessel = Vessel(
            vessel_name=form.vessel_name.data,
            imo_number=form.imo_number.data or None,
            build_year=form.build_year.data or None,
            vessel_type=form.vessel_type.data,
            gross_tonnage_gt=form.gross_tonnage_gt.data or None,
            flag_state=form.flag_state.data,
            uscg_documentation=form.uscg_documentation.data or None,
            radar_system=form.radar_system.data or None,
            route_type=form.route_type.data
        )
        db.session.add(vessel)
        db.session.commit()
        flash(f'Vessel {vessel.vessel_name} created!', 'success')
        return redirect(url_for('vessels.vessels_page'))
    return render_template('vessel_form.html', form=form, action='Create')

@vessels_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@admin_required
def update_vessel(id):
    vessel = Vessel.query.get_or_404(id)
    form = VesselForm(obj=vessel)
    if form.validate_on_submit():
        vessel.vessel_name = form.vessel_name.data
        vessel.imo_number = form.imo_number.data or None
        vessel.build_year = form.build_year.data or None
        vessel.vessel_type = form.vessel_type.data
        vessel.gross_tonnage_gt = form.gross_tonnage_gt.data or None
        vessel.flag_state = form.flag_state.data
        vessel.uscg_documentation = form.uscg_documentation.data or None
        vessel.radar_system = form.radar_system.data or None
        vessel.route_type = form.route_type.data
        db.session.commit()
        flash(f'Vessel {vessel.vessel_name} updated!', 'success')
        return redirect(url_for('vessels.vessels_page'))
    return render_template('vessel_form.html', form=form, vessel=vessel, action='Edit')

@vessels_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_vessel(id):
    vessel = Vessel.query.get_or_404(id)
    db.session.delete(vessel)
    db.session.commit()
    flash(f'Vessel {vessel.vessel_name} deleted!', 'success')
    return redirect(url_for('vessels.vessels_page'))
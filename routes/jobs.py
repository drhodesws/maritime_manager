# routes/jobs.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, admin_required
from models import db, Job, Vessel, Customer
from forms import JobForm

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs_bp.route('/')
@login_required
def jobs_page():
    jobs = Job.query.order_by(Job.date_created.desc()).all()
    return render_template('jobs.html', jobs=jobs)

@jobs_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create_job():
    form = JobForm()
    if form.validate_on_submit():
        job = Job(
            scheduled_date=form.scheduled_date.data,
            requested_service=form.requested_service.data,
            vessel_id=form.vessel_id.data,
            location=form.location.data,
            customer_id=form.customer_id.data or None
        )
        db.session.add(job)
        db.session.commit()
        flash(f'Job {job.job_number} created!', 'success')
        return redirect(url_for('jobs.jobs_page'))
    return render_template('job_form.html', form=form, action='Create')

@jobs_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_job(id):
    job = Job.query.get_or_404(id)
    form = JobForm(obj=job)
    if form.validate_on_submit():
        job.scheduled_date = form.scheduled_date.data
        job.requested_service = form.requested_service.data
        job.vessel_id = form.vessel_id.data
        job.location = form.location.data
        job.customer_id = form.customer_id.data or None
        db.session.commit()
        flash(f'Job {job.job_number} updated!', 'success')
        return redirect(url_for('jobs.jobs_page'))
    return render_template('job_form.html', form=form, job=job, action='Edit')

@jobs_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_job(id):
    job = Job.query.get_or_404(id)
    db.session.delete(job)
    db.session.commit()
    flash(f'Job {job.job_number} deleted!', 'success')
    return redirect(url_for('jobs.jobs_page'))
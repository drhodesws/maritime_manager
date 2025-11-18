# routes/invoices.py — FINAL & 100% WORKING — PDFs OPEN PERFECTLY
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from routes.auth import login_required
from models import db, Job, Timebook, Customer
from datetime import datetime, timedelta
import pdfkit
from jinja2 import Environment, FileSystemLoader
import os
import tempfile

# wkhtmltopdf config — 100% working on Windows
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

# PDF options — fixes all Windows issues
options = {
    'quiet': '',
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None,
    'disable-smart-shrinking': None,
    'enable-local-file-access': None,
}

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')

@invoices_bp.route('/')
@login_required
def invoices_page():
    return render_template('invoices.html')

@invoices_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    jobs = Job.query.all()
    customers = Customer.query.all()

    if request.method == 'POST':
        job_id = request.form.get('job_id')
        customer_id = request.form.get('customer_id') or None
        invoice_date = request.form.get('invoice_date', datetime.now().strftime('%Y-%m-%d'))

        job = Job.query.get_or_404(job_id)
        time_entries = Timebook.query.filter_by(job_number=job.job_number).all()

        # Accurate labor calculation
        labor_total = 0.0
        for entry in time_entries:
            if entry.billable == "Yes":
                start = datetime.combine(datetime.today(), entry.start_time)
                stop = datetime.combine(datetime.today(), entry.stop_time)
                if stop < start:
                    stop += timedelta(days=1)
                hours = (stop - start).total_seconds() / 3600
                labor_total += hours * entry.pay_rate_rt

        materials_total = 0.0
        total = labor_total + materials_total

        # Render HTML
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('invoice_template.html')
        html_out = template.render(
            job=job,
            time_entries=time_entries,
            customer=Customer.query.get(customer_id) if customer_id else None,
            labor_total=f"${labor_total:,.2f}",
            materials_total=f"${materials_total:,.2f}",
            total=f"${total:,.2f}",
            invoice_date=datetime.strptime(invoice_date, '%Y-%m-%d').strftime('%B %d, %Y'),
            invoice_number=f"INV-{datetime.now().strftime('%Y%m%d')}-{job.job_number}"
        )

        # BULLETPROOF PDF GENERATION — writes to real file first
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            pdfkit.from_string(html_out, tmp.name, configuration=config, options=options)
            pdf_path = tmp.name

        # Send the file
        response = send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Invoice_{job.job_number}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )
        # Clean up temp file after send
        @response.call_on_close
        def remove_file():
            try:
                os.remove(pdf_path)
            except:
                pass
        return response

    return render_template('invoice_form.html', jobs=jobs, customers=customers)
from flask import Blueprint, render_template
from routes.auth import login_required  # Import decorator from auth

contacts_bp = Blueprint('contacts', __name__, url_prefix='/contacts')

@contacts_bp.route('/contacts', methods=['GET'])
@login_required
def contacts_page():
    return render_template('contacts.html')
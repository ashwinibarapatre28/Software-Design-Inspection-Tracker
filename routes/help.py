from flask import Blueprint, render_template
from routes.auth import login_required

help_bp = Blueprint('help', __name__, url_prefix='/help')

@help_bp.route('/')
@login_required
def index():
    return render_template('help/index.html')

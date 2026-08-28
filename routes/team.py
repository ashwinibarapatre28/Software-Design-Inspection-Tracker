from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, roles_required
from models import db, User, Defect

team_bp = Blueprint('team', __name__, url_prefix='/team')

@team_bp.route('/')
@login_required
def index():
    users = User.query.order_by(User.name.asc()).all()

    user_stats = []
    for user in users:
        assigned = Defect.query.filter_by(assigned_to_id=user.id).count()
        open_tasks = Defect.query.filter(Defect.assigned_to_id == user.id, Defect.status.in_(['New', 'Assigned', 'In Progress', 'Reopened'])).count()
        resolved = Defect.query.filter(Defect.assigned_to_id == user.id, Defect.status.in_(['Resolved', 'Closed'])).count()
        reported = Defect.query.filter_by(reported_by_id=user.id).count()

        user_stats.append({
            'user': user,
            'assigned': assigned,
            'open_tasks': open_tasks,
            'resolved': resolved,
            'reported': reported
        })

    return render_template('team/index.html', user_stats=user_stats)

@team_bp.route('/<int:user_id>/role', methods=['POST'])
@login_required
@roles_required('Admin')
def update_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role in ['Admin', 'Project Manager', 'Reviewer', 'Developer']:
        user.role = new_role
        db.session.commit()
        flash(f'Role for {user.name} updated to {new_role}.', 'success')
    return redirect(url_for('team.index'))

@team_bp.route('/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@roles_required('Admin')
def toggle_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.status == 'Active':
        user.status = 'Disabled'
        flash(f'Account for {user.name} has been disabled.', 'warning')
    else:
        user.status = 'Active'
        flash(f'Account for {user.name} has been activated.', 'success')
    db.session.commit()
    return redirect(url_for('team.index'))

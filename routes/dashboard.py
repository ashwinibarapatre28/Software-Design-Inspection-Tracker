from flask import Blueprint, render_template, session
from routes.auth import login_required
from models import db, Project, Document, Inspection, Defect, ActivityLog, User

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_id = session.get('user_id')
    user_role = session.get('user_role')

    total_projects = Project.query.filter(Project.status != 'Archived').count()
    total_documents = Document.query.count()
    
    open_statuses = ['New', 'Assigned', 'In Progress', 'Reopened']
    open_defects = Defect.query.filter(Defect.status.in_(open_statuses)).count()
    
    critical_defects = Defect.query.filter(
        Defect.severity == 'Critical',
        Defect.status != 'Closed'
    ).count()

    resolved_defects = Defect.query.filter(Defect.status.in_(['Resolved', 'Closed'])).count()
    pending_verification = Defect.query.filter(Defect.status.in_(['Under Verification', 'Resolved'])).count()

    # My tasks count
    my_tasks_count = Defect.query.filter(
        Defect.assigned_to_id == user_id,
        Defect.status != 'Closed'
    ).count()

    # Recent Defects
    recent_defects = Defect.query.order_by(Defect.updated_at.desc()).limit(7).all()

    # Recent Activity Feed
    recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(8).all()

    # Status Breakdown Counts for quick mini-chart
    status_counts = {
        'New': Defect.query.filter_by(status='New').count(),
        'Assigned': Defect.query.filter_by(status='Assigned').count(),
        'In Progress': Defect.query.filter_by(status='In Progress').count(),
        'Resolved': Defect.query.filter_by(status='Resolved').count(),
        'Under Verification': Defect.query.filter_by(status='Under Verification').count(),
        'Closed': Defect.query.filter_by(status='Closed').count(),
        'Reopened': Defect.query.filter_by(status='Reopened').count()
    }

    # Severity Counts
    severity_counts = {
        'Critical': Defect.query.filter_by(severity='Critical').count(),
        'High': Defect.query.filter_by(severity='High').count(),
        'Medium': Defect.query.filter_by(severity='Medium').count(),
        'Low': Defect.query.filter_by(severity='Low').count(),
        'Cosmetic': Defect.query.filter_by(severity='Cosmetic').count()
    }

    return render_template(
        'dashboard/index.html',
        total_projects=total_projects,
        total_documents=total_documents,
        open_defects=open_defects,
        critical_defects=critical_defects,
        resolved_defects=resolved_defects,
        pending_verification=pending_verification,
        my_tasks_count=my_tasks_count,
        recent_defects=recent_defects,
        recent_activities=recent_activities,
        status_counts=status_counts,
        severity_counts=severity_counts
    )

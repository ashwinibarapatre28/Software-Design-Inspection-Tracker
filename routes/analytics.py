from flask import Blueprint, render_template, jsonify
from routes.auth import login_required
from models import db, Project, Document, Inspection, Defect, Category, User
from routes.reports import calculate_metrics

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def index():
    metrics = calculate_metrics()

    # Total counts
    total_projects = Project.query.filter(Project.status != 'Archived').count()
    total_docs = Document.query.count()
    total_inspections = Inspection.query.count()

    return render_template(
        'analytics/index.html',
        metrics=metrics,
        total_projects=total_projects,
        total_docs=total_docs,
        total_inspections=total_inspections
    )

@analytics_bp.route('/data')
@login_required
def chart_data():
    # 1. Defects by Severity
    severities = ['Critical', 'High', 'Medium', 'Low', 'Cosmetic']
    severity_data = [Defect.query.filter_by(severity=s).count() for s in severities]

    # 2. Defects by Category
    categories = Category.query.all()
    cat_labels = [c.name for c in categories]
    cat_data = [Defect.query.filter_by(category_id=c.id).count() for c in categories]

    # 3. Defects by Status
    statuses = ['New', 'Assigned', 'In Progress', 'Resolved', 'Under Verification', 'Closed', 'Reopened']
    status_data = [Defect.query.filter_by(status=s).count() for s in statuses]

    # 4. Defects by Project
    projects = Project.query.filter(Project.status != 'Archived').all()
    project_labels = [p.name for p in projects]
    project_data = [Defect.query.filter_by(project_id=p.id).count() for p in projects]

    return jsonify({
        'severity': {
            'labels': severities,
            'data': severity_data
        },
        'category': {
            'labels': cat_labels,
            'data': cat_data
        },
        'status': {
            'labels': statuses,
            'data': status_data
        },
        'project': {
            'labels': project_labels,
            'data': project_data
        }
    })

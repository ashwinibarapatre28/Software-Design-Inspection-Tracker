import csv
import json
from io import StringIO
from datetime import datetime
from flask import Blueprint, render_template, request, make_response, jsonify, flash
from routes.auth import login_required
from models import db, Project, Document, Inspection, Defect, User, Category

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

def calculate_metrics(project_id=None, doc_id=None):
    defect_query = Defect.query
    doc_query = Document.query

    if project_id:
        defect_query = defect_query.filter_by(project_id=project_id)
        doc_query = doc_query.filter_by(project_id=project_id)
    if doc_id:
        defect_query = defect_query.filter_by(document_id=doc_id)
        doc_query = doc_query.filter_by(id=doc_id)

    defects = defect_query.all()
    documents = doc_query.all()

    total_defects = len(defects)
    closed_defects = len([d for d in defects if d.status == 'Closed'])
    resolved_defects = len([d for d in defects if d.status in ['Resolved', 'Closed', 'Under Verification']])
    
    # Calculate Total Document Size (Pages or LOC)
    total_doc_size = sum([d.size_metric_value for d in documents]) if documents else 100.0

    # 1. Defect Density = Number of Defects / Document Size
    defect_density = (total_defects / total_doc_size) if total_doc_size > 0 else 0.0

    # 2. Defect Removal Efficiency (DRE) = (Defects Removed / Total Defects) * 100
    dre_percentage = ((resolved_defects / total_defects) * 100) if total_defects > 0 else 100.0

    # 3. Defect Closure Rate = (Closed Defects / Total Defects) * 100
    closure_rate = ((closed_defects / total_defects) * 100) if total_defects > 0 else 100.0

    # 4. Average Resolution Time (Hours / Days)
    resolved_times = []
    for d in defects:
        if d.resolved_at and d.created_at:
            delta_days = (d.resolved_at - d.created_at).total_seconds() / (24 * 3600)
            resolved_times.append(delta_days)

    avg_resolution_time = (sum(resolved_times) / len(resolved_times)) if resolved_times else 0.0

    return {
        'total_defects': total_defects,
        'closed_defects': closed_defects,
        'resolved_defects': resolved_defects,
        'total_doc_size': round(total_doc_size, 1),
        'defect_density': round(defect_density, 3),
        'dre_percentage': round(dre_percentage, 1),
        'closure_rate': round(closure_rate, 1),
        'avg_resolution_time': round(avg_resolution_time, 1)
    }

@reports_bp.route('/')
@login_required
def index():
    report_type = request.args.get('type', 'Project Defect Report')
    project_id = request.args.get('project_id', type=int)
    document_id = request.args.get('document_id', type=int)

    projects = Project.query.filter(Project.status != 'Archived').all()
    documents = Document.query.all()

    query = Defect.query

    if project_id:
        query = query.filter_by(project_id=project_id)
    if document_id:
        query = query.filter_by(document_id=document_id)

    if report_type == 'Open Defects Report':
        query = query.filter(Defect.status.in_(['New', 'Assigned', 'In Progress', 'Reopened']))
    elif report_type == 'Critical Defects Report':
        query = query.filter_by(severity='Critical')

    defects = query.order_by(Defect.created_at.desc()).all()
    metrics = calculate_metrics(project_id, document_id)

    selected_project = Project.query.get(project_id) if project_id else None
    selected_doc = Document.query.get(document_id) if document_id else None

    # Severity Counts
    critical_count = len([d for d in defects if d.severity == 'Critical'])
    high_count = len([d for d in defects if d.severity == 'High'])
    medium_count = len([d for d in defects if d.severity == 'Medium'])
    low_count = len([d for d in defects if d.severity == 'Low'])
    cosmetic_count = len([d for d in defects if d.severity == 'Cosmetic'])

    return render_template(
        'reports/index.html',
        report_type=report_type,
        projects=projects,
        documents=documents,
        selected_project=selected_project,
        selected_doc=selected_doc,
        defects=defects,
        metrics=metrics,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        cosmetic_count=cosmetic_count
    )

@reports_bp.route('/export/csv')
@login_required
def export_csv():
    project_id = request.args.get('project_id', type=int)
    query = Defect.query
    if project_id:
        query = query.filter_by(project_id=project_id)

    defects = query.all()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow([
        'Defect ID', 'Title', 'Project', 'Document', 'Version', 'Category',
        'Severity', 'Priority', 'Status', 'Location', 'Reported By',
        'Assigned To', 'Created Date', 'Due Date'
    ])

    for d in defects:
        cw.writerow([
            d.defect_code,
            d.title,
            d.project.name if d.project else '',
            d.document.name if d.document else '',
            d.document_version,
            d.category.name if d.category else '',
            d.severity,
            d.priority,
            d.status,
            d.location or '',
            d.reporter.name if d.reporter else '',
            d.assignee.name if d.assignee else 'Unassigned',
            d.created_at.strftime('%Y-%m-%d'),
            d.due_date.strftime('%Y-%m-%d') if d.due_date else ''
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=designinspect_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@reports_bp.route('/export/json')
@login_required
def export_json():
    project_id = request.args.get('project_id', type=int)
    query = Defect.query
    if project_id:
        query = query.filter_by(project_id=project_id)

    defects = query.all()

    data = []
    for d in defects:
        data.append({
            'defect_code': d.defect_code,
            'title': d.title,
            'project': d.project.name if d.project else None,
            'document': d.document.name if d.document else None,
            'version': d.document_version,
            'category': d.category.name if d.category else None,
            'severity': d.severity,
            'priority': d.priority,
            'status': d.status,
            'location': d.location,
            'reported_by': d.reporter.name if d.reporter else None,
            'assigned_to': d.assignee.name if d.assignee else None,
            'created_at': d.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    response = make_response(json.dumps(data, indent=2))
    response.headers["Content-Disposition"] = f"attachment; filename=designinspect_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    response.headers["Content-type"] = "application/json"
    return response

@reports_bp.route('/print-pdf')
@login_required
def print_pdf():
    project_id = request.args.get('project_id', type=int)
    document_id = request.args.get('document_id', type=int)

    query = Defect.query
    if project_id:
        query = query.filter_by(project_id=project_id)
    if document_id:
        query = query.filter_by(document_id=document_id)

    defects = query.order_by(Defect.created_at.desc()).all()
    metrics = calculate_metrics(project_id, document_id)

    selected_project = Project.query.get(project_id) if project_id else None
    selected_doc = Document.query.get(document_id) if document_id else None

    return render_template(
        'reports/print_pdf.html',
        defects=defects,
        metrics=metrics,
        selected_project=selected_project,
        selected_doc=selected_doc,
        generated_at=datetime.now().strftime('%B %d, %Y - %H:%M')
    )

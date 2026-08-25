from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from models import db, Inspection, Project, Document, User, Defect

inspections_bp = Blueprint('inspections', __name__, url_prefix='/inspections')

@inspections_bp.route('/')
@login_required
def index():
    project_id = request.args.get('project_id', type=int)
    type_filter = request.args.get('type', 'all')
    status_filter = request.args.get('status', 'all')

    query = Inspection.query

    if project_id:
        query = query.filter_by(project_id=project_id)
    if type_filter != 'all':
        query = query.filter_by(inspection_type=type_filter)
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    inspections = query.order_by(Inspection.inspection_date.desc()).all()
    projects = Project.query.filter(Project.status != 'Archived').all()

    return render_template(
        'inspections/index.html',
        inspections=inspections,
        projects=projects,
        selected_project=project_id,
        type_filter=type_filter,
        status_filter=status_filter
    )

@inspections_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        project_id = request.form.get('project_id', type=int)
        document_id = request.form.get('document_id', type=int)
        inspection_type = request.form.get('inspection_type')
        lead_reviewer_id = request.form.get('lead_reviewer_id', type=int)
        review_team = request.form.get('review_team', '').strip()
        inspection_date_str = request.form.get('inspection_date')
        status = request.form.get('status', 'Scheduled')
        summary = request.form.get('summary', '').strip()

        doc = Document.query.get_or_404(document_id)

        # Generate inspection code (INS-xxx)
        last_insp = Inspection.query.order_by(Inspection.id.desc()).first()
        new_id_num = (last_insp.id + 1) if last_insp else 1
        inspection_code = f"INS-{new_id_num:03d}"

        inspection_date = datetime.strptime(inspection_date_str, '%Y-%m-%d').date() if inspection_date_str else datetime.utcnow().date()

        inspection = Inspection(
            inspection_code=inspection_code,
            project_id=project_id,
            document_id=document_id,
            document_version=doc.version,
            inspection_type=inspection_type,
            lead_reviewer_id=lead_reviewer_id,
            review_team=review_team,
            inspection_date=inspection_date,
            status=status,
            summary=summary
        )

        db.session.add(inspection)
        db.session.commit()

        flash(f'Inspection {inspection_code} scheduled successfully!', 'success')
        return redirect(url_for('inspections.detail', inspection_id=inspection.id))

    projects = Project.query.filter(Project.status != 'Archived').all()
    documents = Document.query.all()
    reviewers = User.query.filter(User.role.in_(['Reviewer', 'Admin', 'Project Manager'])).all()

    return render_template(
        'inspections/form.html',
        action='Create',
        inspection=None,
        projects=projects,
        documents=documents,
        reviewers=reviewers
    )

@inspections_bp.route('/<int:inspection_id>')
@login_required
def detail(inspection_id):
    inspection = Inspection.query.get_or_404(inspection_id)
    defects = Defect.query.filter_by(inspection_id=inspection.id).order_by(Defect.created_at.desc()).all()

    critical_count = len([d for d in defects if d.severity == 'Critical'])
    high_count = len([d for d in defects if d.severity == 'High'])
    closed_count = len([d for d in defects if d.status == 'Closed'])

    return render_template(
        'inspections/detail.html',
        inspection=inspection,
        defects=defects,
        critical_count=critical_count,
        high_count=high_count,
        closed_count=closed_count
    )

@inspections_bp.route('/<int:inspection_id>/status', methods=['POST'])
@login_required
def update_status(inspection_id):
    inspection = Inspection.query.get_or_404(inspection_id)
    new_status = request.form.get('status')
    if new_status:
        inspection.status = new_status
        db.session.commit()
        flash(f'Inspection status updated to "{new_status}".', 'success')
    return redirect(url_for('inspections.detail', inspection_id=inspection.id))

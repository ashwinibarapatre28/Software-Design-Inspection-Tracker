import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename
from routes.auth import login_required
from models import db, Document, Project, User, Inspection, Defect

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'txt', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/')
@login_required
def index():
    project_id = request.args.get('project_id', type=int)
    type_filter = request.args.get('type', 'all')
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '').strip()

    query = Document.query

    if project_id:
        query = query.filter_by(project_id=project_id)
    if type_filter != 'all':
        query = query.filter_by(document_type=type_filter)
    if status_filter != 'all':
        query = query.filter_by(review_status=status_filter)
    if search_query:
        query = query.filter(
            (Document.name.ilike(f'%{search_query}%')) |
            (Document.doc_code.ilike(f'%{search_query}%'))
        )

    documents = query.order_by(Document.upload_date.desc()).all()
    projects = Project.query.filter(Project.status != 'Archived').all()

    return render_template(
        'documents/index.html',
        documents=documents,
        projects=projects,
        selected_project=project_id,
        type_filter=type_filter,
        status_filter=status_filter,
        search_query=search_query
    )

@documents_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        project_id = request.form.get('project_id', type=int)
        name = request.form.get('name', '').strip()
        document_type = request.form.get('document_type')
        version = request.form.get('version', 'v1.0').strip()
        reviewer_id = request.form.get('reviewer_id', type=int)
        size_type = request.form.get('size_metric_type', 'Pages')
        size_value = request.form.get('size_metric_value', type=float) or 10.0

        if not project_id or not name or not document_type:
            flash('Project, Document Name, and Document Type are required.', 'danger')
            return redirect(url_for('documents.create'))

        # Auto-generate document code
        last_doc = Document.query.order_by(Document.id.desc()).first()
        new_id_num = (last_doc.id + 1) if last_doc else 201
        doc_code = f"DOC-{new_id_num}"

        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{doc_code}_{file.filename}")
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join('uploads', filename)
                file.save(os.path.join(upload_folder, filename))

        doc = Document(
            doc_code=doc_code,
            project_id=project_id,
            name=name,
            document_type=document_type,
            version=version,
            author_id=session.get('user_id'),
            reviewer_id=reviewer_id,
            review_status='Not Reviewed',
            size_metric_type=size_type,
            size_metric_value=size_value,
            file_path=file_path
        )

        db.session.add(doc)
        db.session.commit()

        flash(f'Design Document {doc_code} registered successfully!', 'success')
        return redirect(url_for('documents.detail', doc_id=doc.id))

    projects = Project.query.filter(Project.status != 'Archived').all()
    reviewers = User.query.filter(User.role.in_(['Reviewer', 'Admin', 'Project Manager'])).all()

    return render_template('documents/form.html', action='Register', doc=None, projects=projects, reviewers=reviewers)

@documents_bp.route('/<int:doc_id>')
@login_required
def detail(doc_id):
    doc = Document.query.get_or_404(doc_id)
    inspections = Inspection.query.filter_by(document_id=doc.id).all()
    defects = Defect.query.filter_by(document_id=doc.id).order_by(Defect.created_at.desc()).all()

    # Find version history (other documents with same name or code prefix in same project)
    version_history = Document.query.filter(
        Document.project_id == doc.project_id,
        Document.name == doc.name
    ).order_by(Document.version.desc()).all()

    return render_template(
        'documents/detail.html',
        doc=doc,
        inspections=inspections,
        defects=defects,
        version_history=version_history
    )

@documents_bp.route('/<int:doc_id>/status', methods=['POST'])
@login_required
def update_status(doc_id):
    doc = Document.query.get_or_404(doc_id)
    new_status = request.form.get('review_status')
    if new_status:
        doc.review_status = new_status
        db.session.commit()
        flash(f'Document review status updated to "{new_status}".', 'success')
    return redirect(url_for('documents.detail', doc_id=doc.id))

@documents_bp.route('/<int:doc_id>/new-version', methods=['GET', 'POST'])
@login_required
def create_version(doc_id):
    existing_doc = Document.query.get_or_404(doc_id)
    if request.method == 'POST':
        new_version = request.form.get('version', '').strip()
        size_type = request.form.get('size_metric_type', existing_doc.size_metric_type)
        size_value = request.form.get('size_metric_value', type=float) or existing_doc.size_metric_value

        last_doc = Document.query.order_by(Document.id.desc()).first()
        new_id_num = (last_doc.id + 1) if last_doc else 201
        doc_code = f"DOC-{new_id_num}"

        file_path = existing_doc.file_path
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{doc_code}_{file.filename}")
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join('uploads', filename)
                file.save(os.path.join(upload_folder, filename))

        new_doc = Document(
            doc_code=doc_code,
            project_id=existing_doc.project_id,
            name=existing_doc.name,
            document_type=existing_doc.document_type,
            version=new_version,
            author_id=session.get('user_id'),
            reviewer_id=existing_doc.reviewer_id,
            review_status='Not Reviewed',
            size_metric_type=size_type,
            size_metric_value=size_value,
            file_path=file_path
        )

        db.session.add(new_doc)
        db.session.commit()

        flash(f'New document version {new_version} created successfully!', 'success')
        return redirect(url_for('documents.detail', doc_id=new_doc.id))

    return render_template('documents/new_version.html', existing_doc=existing_doc)

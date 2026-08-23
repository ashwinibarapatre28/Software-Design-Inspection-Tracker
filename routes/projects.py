from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required, roles_required
from models import db, Project, User, Document, Inspection, Defect

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '').strip()

    query = Project.query

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if search_query:
        query = query.filter(
            (Project.name.ilike(f'%{search_query}%')) |
            (Project.project_code.ilike(f'%{search_query}%')) |
            (Project.description.ilike(f'%{search_query}%'))
        )

    projects = query.order_by(Project.created_at.desc()).all()
    all_managers = User.query.filter(User.role.in_(['Project Manager', 'Admin'])).all()

    return render_template('projects/index.html', projects=projects, status_filter=status_filter, search_query=search_query, managers=all_managers)

@projects_bp.route('/new', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Project Manager')
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        manager_id = request.form.get('manager_id', type=int)
        status = request.form.get('status', 'Planning')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        if not name or not manager_id:
            flash('Project Name and Manager are required.', 'danger')
            return redirect(url_for('projects.create'))

        # Auto-generate project code (PRJ-xxx)
        last_project = Project.query.order_by(Project.id.desc()).first()
        new_id_num = (last_project.id + 1) if last_project else 101
        project_code = f"PRJ-{new_id_num}"

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        project = Project(
            project_code=project_code,
            name=name,
            description=description,
            manager_id=manager_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )

        db.session.add(project)
        db.session.commit()

        flash(f'Project {project_code} created successfully!', 'success')
        return redirect(url_for('projects.detail', project_id=project.id))

    managers = User.query.filter(User.role.in_(['Project Manager', 'Admin'])).all()
    return render_template('projects/form.html', action='Create', project=None, managers=managers)

@projects_bp.route('/<int:project_id>')
@login_required
def detail(project_id):
    project = Project.query.get_or_404(project_id)
    documents = Document.query.filter_by(project_id=project.id).all()
    inspections = Inspection.query.filter_by(project_id=project.id).all()
    defects = Defect.query.filter_by(project_id=project.id).order_by(Defect.created_at.desc()).all()

    total_defects = len(defects)
    open_defects = len([d for d in defects if d.status in ['New', 'Assigned', 'In Progress', 'Reopened']])
    critical_defects = len([d for d in defects if d.severity == 'Critical' and d.status != 'Closed'])
    closed_defects = len([d for d in defects if d.status == 'Closed'])

    return render_template(
        'projects/detail.html',
        project=project,
        documents=documents,
        inspections=inspections,
        defects=defects,
        total_defects=total_defects,
        open_defects=open_defects,
        critical_defects=critical_defects,
        closed_defects=closed_defects
    )

@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Project Manager')
def edit(project_id):
    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        project.name = request.form.get('name', '').strip()
        project.description = request.form.get('description', '').strip()
        project.manager_id = request.form.get('manager_id', type=int)
        project.status = request.form.get('status', project.status)
        
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')

        project.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        project.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        db.session.commit()
        flash('Project details updated successfully.', 'success')
        return redirect(url_for('projects.detail', project_id=project.id))

    managers = User.query.filter(User.role.in_(['Project Manager', 'Admin'])).all()
    return render_template('projects/form.html', action='Edit', project=project, managers=managers)

@projects_bp.route('/<int:project_id>/archive', methods=['POST'])
@login_required
@roles_required('Admin', 'Project Manager')
def archive(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = 'Archived'
    db.session.commit()
    flash(f'Project {project.project_code} has been archived.', 'info')
    return redirect(url_for('projects.index'))

import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.utils import secure_filename
from routes.auth import login_required
from models import db, Defect, Project, Document, Inspection, Category, User, Comment, ActivityLog, Notification

defects_bp = Blueprint('defects', __name__, url_prefix='/defects')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'txt', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_activity(defect_id, user_id, action, old_val=None, new_val=None):
    activity = ActivityLog(
        defect_id=defect_id,
        user_id=user_id,
        action=action,
        old_value=str(old_val) if old_val else None,
        new_value=str(new_val) if new_val else None,
        timestamp=datetime.utcnow()
    )
    db.session.add(activity)

def create_notification(user_id, message, notif_type='info', link=None):
    if user_id:
        notif = Notification(
            user_id=user_id,
            message=message,
            notification_type=notif_type,
            link=link
        )
        db.session.add(notif)

@defects_bp.route('/')
@login_required
def index():
    status = request.args.get('status', 'all')
    severity = request.args.get('severity', 'all')
    priority = request.args.get('priority', 'all')
    category_id = request.args.get('category_id', type=int)
    project_id = request.args.get('project_id', type=int)
    assigned_to = request.args.get('assigned_to', type=int)
    search = request.args.get('search', '').strip()

    query = Defect.query

    if status != 'all':
        query = query.filter_by(status=status)
    if severity != 'all':
        query = query.filter_by(severity=severity)
    if priority != 'all':
        query = query.filter_by(priority=priority)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if project_id:
        query = query.filter_by(project_id=project_id)
    if assigned_to:
        query = query.filter_by(assigned_to_id=assigned_to)

    if search:
        query = query.filter(
            (Defect.defect_code.ilike(f'%{search}%')) |
            (Defect.title.ilike(f'%{search}%')) |
            (Defect.description.ilike(f'%{search}%')) |
            (Defect.location.ilike(f'%{search}%'))
        )

    defects = query.order_by(Defect.updated_at.desc()).all()

    categories = Category.query.all()
    projects = Project.query.filter(Project.status != 'Archived').all()
    team_members = User.query.filter(User.status == 'Active').all()

    return render_template(
        'defects/index.html',
        defects=defects,
        categories=categories,
        projects=projects,
        team_members=team_members,
        status=status,
        severity=severity,
        priority=priority,
        category_id=category_id,
        project_id=project_id,
        assigned_to=assigned_to,
        search=search
    )

@defects_bp.route('/kanban')
@login_required
def kanban():
    project_id = request.args.get('project_id', type=int)
    query = Defect.query

    if project_id:
        query = query.filter_by(project_id=project_id)

    all_defects = query.order_by(Defect.updated_at.desc()).all()

    kanban_columns = {
        'New': [d for d in all_defects if d.status == 'New'],
        'Assigned': [d for d in all_defects if d.status == 'Assigned'],
        'In Progress': [d for d in all_defects if d.status == 'In Progress'],
        'Resolved': [d for d in all_defects if d.status == 'Resolved'],
        'Under Verification': [d for d in all_defects if d.status == 'Under Verification'],
        'Closed': [d for d in all_defects if d.status in ['Closed', 'Rejected']]
    }

    projects = Project.query.filter(Project.status != 'Archived').all()

    return render_template(
        'defects/kanban.html',
        kanban_columns=kanban_columns,
        projects=projects,
        selected_project=project_id
    )

@defects_bp.route('/my-tasks')
@login_required
def my_tasks():
    user_id = session.get('user_id')
    my_defects = Defect.query.filter_by(assigned_to_id=user_id).order_by(Defect.updated_at.desc()).all()

    open_tasks = [d for d in my_defects if d.status not in ['Closed', 'Rejected']]
    completed_tasks = [d for d in my_defects if d.status in ['Closed', 'Resolved', 'Under Verification']]

    return render_template(
        'defects/my_tasks.html',
        open_tasks=open_tasks,
        completed_tasks=completed_tasks
    )

@defects_bp.route('/log', methods=['GET', 'POST'])
@defects_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        project_id = request.form.get('project_id', type=int)
        document_id = request.form.get('document_id', type=int)
        inspection_id = request.form.get('inspection_id', type=int) or None
        
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category_id = request.form.get('category_id', type=int)
        severity = request.form.get('severity')
        priority = request.form.get('priority')
        
        location = request.form.get('location', '').strip()
        page_section = request.form.get('page_section', '').strip()
        assigned_to_id = request.form.get('assigned_to_id', type=int) or None
        
        recommended_fix = request.form.get('recommended_fix', '').strip()
        reviewer_comments = request.form.get('reviewer_comments', '').strip()
        due_date_str = request.form.get('due_date')

        doc = Document.query.get_or_404(document_id)

        # Generate unique defect code DEF-xxxxx
        last_defect = Defect.query.order_by(Defect.id.desc()).first()
        new_num = (last_defect.id + 1) if last_defect else 125
        defect_code = f"DEF-{new_num:05d}"

        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None

        attachment_path = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{defect_code}_{file.filename}")
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                attachment_path = os.path.join('uploads', filename)
                file.save(os.path.join(upload_folder, filename))

        initial_status = 'Assigned' if assigned_to_id else 'New'

        defect = Defect(
            defect_code=defect_code,
            inspection_id=inspection_id,
            document_id=document_id,
            document_version=doc.version,
            project_id=project_id,
            title=title,
            description=description,
            category_id=category_id,
            severity=severity,
            priority=priority,
            status=initial_status,
            location=location,
            page_section=page_section,
            reported_by_id=session.get('user_id'),
            assigned_to_id=assigned_to_id,
            recommended_fix=recommended_fix,
            reviewer_comments=reviewer_comments,
            due_date=due_date,
            attachment_path=attachment_path
        )

        db.session.add(defect)
        db.session.flush()

        log_activity(defect.id, session.get('user_id'), "Defect Created", old_val=None, new_val=initial_status)
        
        if assigned_to_id:
            assignee = User.query.get(assigned_to_id)
            log_activity(defect.id, session.get('user_id'), "Assigned to Developer", old_val="Unassigned", new_val=assignee.name if assignee else str(assigned_to_id))
            create_notification(assigned_to_id, f"You were assigned defect {defect_code}: {title}", "assignment", f"/defects/{defect.id}")

        db.session.commit()

        flash(f'Defect {defect_code} logged successfully!', 'success')
        return redirect(url_for('defects.detail', defect_id=defect.id))

    projects = Project.query.filter(Project.status != 'Archived').all()
    documents = Document.query.all()
    inspections = Inspection.query.all()
    categories = Category.query.all()
    team_members = User.query.filter(User.status == 'Active').all()

    return render_template(
        'defects/form.html',
        action='Log',
        defect=None,
        projects=projects,
        documents=documents,
        inspections=inspections,
        categories=categories,
        team_members=team_members
    )

@defects_bp.route('/<int:defect_id>')
@login_required
def detail(defect_id):
    defect = Defect.query.get_or_404(defect_id)
    comments = Comment.query.filter_by(defect_id=defect.id, parent_id=None).order_by(Comment.created_at.asc()).all()
    activities = ActivityLog.query.filter_by(defect_id=defect.id).order_by(ActivityLog.timestamp.asc()).all()
    team_members = User.query.filter(User.status == 'Active').all()

    return render_template(
        'defects/detail.html',
        defect=defect,
        comments=comments,
        activities=activities,
        team_members=team_members
    )

@defects_bp.route('/<int:defect_id>/status', methods=['POST'])
@login_required
def update_status(defect_id):
    defect = Defect.query.get_or_404(defect_id)
    new_status = request.form.get('status')
    resolution_comment = request.form.get('resolution_comment', '').strip()
    user_id = session.get('user_id')

    if not new_status:
        flash('Invalid status provided.', 'danger')
        return redirect(url_for('defects.detail', defect_id=defect.id))

    old_status = defect.status
    defect.status = new_status
    defect.updated_at = datetime.utcnow()

    if new_status == 'Resolved':
        defect.resolved_at = datetime.utcnow()
        if resolution_comment:
            defect.developer_comments = resolution_comment

    elif new_status == 'Closed':
        defect.closed_at = datetime.utcnow()

    log_activity(defect.id, user_id, "Status Changed", old_val=old_status, new_val=new_status)

    # Add resolution comment if present
    if resolution_comment:
        comment = Comment(
            defect_id=defect.id,
            user_id=user_id,
            comment_text=f"**Status transition to {new_status}**: {resolution_comment}"
        )
        db.session.add(comment)

    # Trigger notifications
    if new_status in ['Resolved', 'Under Verification']:
        create_notification(
            defect.reported_by_id,
            f"Defect {defect.defect_code} marked as {new_status} and ready for verification.",
            "status_change",
            f"/defects/{defect.id}"
        )
    elif new_status in ['In Progress', 'Assigned', 'Closed', 'Reopened']:
        if defect.assigned_to_id:
            create_notification(
                defect.assigned_to_id,
                f"Status of defect {defect.defect_code} changed to {new_status}.",
                "status_change",
                f"/defects/{defect.id}"
            )

    db.session.commit()
    flash(f'Status updated to "{new_status}".', 'success')
    return redirect(url_for('defects.detail', defect_id=defect.id))

@defects_bp.route('/<int:defect_id>/reopen', methods=['POST'])
@login_required
def reopen(defect_id):
    defect = Defect.query.get_or_404(defect_id)
    reason = request.form.get('reason', '').strip()
    user_id = session.get('user_id')

    if not reason:
        flash('Reopening reason is required.', 'danger')
        return redirect(url_for('defects.detail', defect_id=defect.id))

    old_status = defect.status
    defect.status = 'Reopened'
    defect.updated_at = datetime.utcnow()

    log_activity(defect.id, user_id, "Defect Reopened", old_val=old_status, new_val="Reopened")

    # Add comment with reason
    comment = Comment(
        defect_id=defect.id,
        user_id=user_id,
        comment_text=f"🚨 **Defect Reopened by Reviewer**: {reason}"
    )
    db.session.add(comment)

    if defect.assigned_to_id:
        create_notification(
            defect.assigned_to_id,
            f"Defect {defect.defect_code} was REOPENED by reviewer. Reason: {reason}",
            "status_change",
            f"/defects/{defect.id}"
        )

    db.session.commit()
    flash('Defect has been reopened.', 'warning')
    return redirect(url_for('defects.detail', defect_id=defect.id))

@defects_bp.route('/<int:defect_id>/assign', methods=['POST'])
@login_required
def assign(defect_id):
    defect = Defect.query.get_or_404(defect_id)
    assigned_to_id = request.form.get('assigned_to_id', type=int)
    user_id = session.get('user_id')

    old_assignee = defect.assignee.name if defect.assignee else "Unassigned"
    defect.assigned_to_id = assigned_to_id

    if defect.status == 'New':
        defect.status = 'Assigned'

    new_assignee = User.query.get(assigned_to_id)
    new_assignee_name = new_assignee.name if new_assignee else str(assigned_to_id)

    log_activity(defect.id, user_id, "Assigned to Developer", old_val=old_assignee, new_val=new_assignee_name)
    create_notification(assigned_to_id, f"You were assigned defect {defect.defect_code}: {defect.title}", "assignment", f"/defects/{defect.id}")

    db.session.commit()
    flash(f'Defect assigned to {new_assignee_name}.', 'success')
    return redirect(url_for('defects.detail', defect_id=defect.id))

@defects_bp.route('/<int:defect_id>/comment', methods=['POST'])
@login_required
def add_comment(defect_id):
    defect = Defect.query.get_or_404(defect_id)
    comment_text = request.form.get('comment_text', '').strip()
    parent_id = request.form.get('parent_id', type=int) or None
    user_id = session.get('user_id')

    if comment_text:
        comment = Comment(
            defect_id=defect.id,
            user_id=user_id,
            parent_id=parent_id,
            comment_text=comment_text
        )
        db.session.add(comment)
        log_activity(defect.id, user_id, "Comment Added", old_val=None, new_val=comment_text[:50])

        # Notify assigned dev & reporter if commenter is someone else
        target_ids = {defect.reported_by_id, defect.assigned_to_id} - {user_id, None}
        current_user_name = session.get('user_name')
        for tid in target_ids:
            create_notification(tid, f"New comment on {defect.defect_code} by {current_user_name}", "comment", f"/defects/{defect.id}")

        db.session.commit()
        flash('Comment posted successfully.', 'success')

    return redirect(url_for('defects.detail', defect_id=defect.id))

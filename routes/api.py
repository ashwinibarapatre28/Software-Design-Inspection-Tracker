from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models import db, Project, Document, Inspection, Defect, User, Notification

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/search')
@login_required
def global_search():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'results': []})

    results = []

    # Search Defects
    defects = Defect.query.filter(
        (Defect.defect_code.ilike(f'%{q}%')) |
        (Defect.title.ilike(f'%{q}%')) |
        (Defect.description.ilike(f'%{q}%'))
    ).limit(5).all()

    for d in defects:
        results.append({
            'type': 'Defect',
            'icon': 'fa-bug',
            'code': d.defect_code,
            'title': d.title,
            'subtitle': f"Status: {d.status} | Severity: {d.severity}",
            'url': f"/defects/{d.id}"
        })

    # Search Projects
    projects = Project.query.filter(
        (Project.project_code.ilike(f'%{q}%')) |
        (Project.name.ilike(f'%{q}%')) |
        (Project.description.ilike(f'%{q}%'))
    ).limit(5).all()

    for p in projects:
        results.append({
            'type': 'Project',
            'icon': 'fa-folder',
            'code': p.project_code,
            'title': p.name,
            'subtitle': f"Status: {p.status}",
            'url': f"/projects/{p.id}"
        })

    # Search Documents
    documents = Document.query.filter(
        (Document.doc_code.ilike(f'%{q}%')) |
        (Document.name.ilike(f'%{q}%'))
    ).limit(5).all()

    for doc in documents:
        results.append({
            'type': 'Document',
            'icon': 'fa-file-code',
            'code': doc.doc_code,
            'title': f"{doc.name} ({doc.version})",
            'subtitle': f"Type: {doc.document_type}",
            'url': f"/documents/{doc.id}"
        })

    # Search Inspections
    inspections = Inspection.query.filter(
        (Inspection.inspection_code.ilike(f'%{q}%')) |
        (Inspection.summary.ilike(f'%{q}%'))
    ).limit(5).all()

    for insp in inspections:
        results.append({
            'type': 'Inspection',
            'icon': 'fa-clipboard-check',
            'code': insp.inspection_code,
            'title': f"{insp.inspection_type} - {insp.inspection_code}",
            'subtitle': f"Date: {insp.inspection_date}",
            'url': f"/inspections/{insp.id}"
        })

    # Search Team Members
    users = User.query.filter(
        (User.name.ilike(f'%{q}%')) |
        (User.username.ilike(f'%{q}%')) |
        (User.email.ilike(f'%{q}%'))
    ).limit(5).all()

    for u in users:
        results.append({
            'type': 'Team Member',
            'icon': 'fa-user-tie',
            'code': u.role,
            'title': u.name,
            'subtitle': u.email,
            'url': f"/team"
        })

    return jsonify({'results': results})

@api_bp.route('/notifications')
@login_required
def get_notifications():
    user_id = session.get('user_id')
    notifications = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc()).limit(10).all()

    unread_count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    data = []
    for n in notifications:
        data.append({
            'id': n.id,
            'message': n.message,
            'type': n.notification_type,
            'link': n.link or '#',
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%b %d, %H:%M')
        })

    return jsonify({'unread_count': unread_count, 'notifications': data})

@api_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_read_all():
    user_id = session.get('user_id')
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})

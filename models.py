from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(60), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='Reviewer') # Admin, Project Manager, Reviewer, Developer
    status = db.Column(db.String(20), nullable=False, default='Active') # Active, Disabled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    managed_projects = db.relationship('Project', backref='manager', foreign_keys='Project.manager_id', lazy=True)
    authored_docs = db.relationship('Document', backref='author', foreign_keys='Document.author_id', lazy=True)
    reviewed_docs = db.relationship('Document', backref='reviewer', foreign_keys='Document.reviewer_id', lazy=True)
    lead_inspections = db.relationship('Inspection', backref='lead_reviewer', foreign_keys='Inspection.lead_reviewer_id', lazy=True)
    reported_defects = db.relationship('Defect', backref='reporter', foreign_keys='Defect.reported_by_id', lazy=True)
    assigned_defects = db.relationship('Defect', backref='assignee', foreign_keys='Defect.assigned_to_id', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'status': self.status
        }


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Active') # Planning, Active, Under Review, Completed, Archived
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    documents = db.relationship('Document', backref='project', cascade='all, delete-orphan', lazy=True)
    inspections = db.relationship('Inspection', backref='project', cascade='all, delete-orphan', lazy=True)
    defects = db.relationship('Defect', backref='project', cascade='all, delete-orphan', lazy=True)


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    doc_code = db.Column(db.String(20), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    document_type = db.Column(db.String(50), nullable=False) # Architecture, DB, API, etc.
    version = db.Column(db.String(20), nullable=False, default='v1.0')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_status = db.Column(db.String(30), nullable=False, default='Not Reviewed') # Not Reviewed, In Review, Review Completed, Revision Required, Approved
    size_metric_type = db.Column(db.String(30), default='Pages') # Pages, Lines of Code, Function Points
    size_metric_value = db.Column(db.Float, default=10.0)
    file_path = db.Column(db.String(255), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    inspections = db.relationship('Inspection', backref='document', cascade='all, delete-orphan', lazy=True)
    defects = db.relationship('Defect', backref='document', cascade='all, delete-orphan', lazy=True)


class Inspection(db.Model):
    __tablename__ = 'inspections'

    id = db.Column(db.Integer, primary_key=True)
    inspection_code = db.Column(db.String(20), unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    document_version = db.Column(db.String(20), nullable=False)
    inspection_type = db.Column(db.String(50), nullable=False) # Formal Design Inspection, Peer Review, etc.
    lead_reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    review_team = db.Column(db.Text, nullable=True) # Stored as comma-separated names or roles
    inspection_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='Scheduled') # Scheduled, In Progress, Completed, Cancelled
    summary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    defects = db.relationship('Defect', backref='inspection', lazy=True)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_custom = db.Column(db.Boolean, default=False)

    defects = db.relationship('Defect', backref='category', lazy=True)


class Defect(db.Model):
    __tablename__ = 'defects'

    id = db.Column(db.Integer, primary_key=True)
    defect_code = db.Column(db.String(20), unique=True, nullable=False)
    inspection_id = db.Column(db.Integer, db.ForeignKey('inspections.id'), nullable=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    document_version = db.Column(db.String(20), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    severity = db.Column(db.String(20), nullable=False) # Critical, High, Medium, Low, Cosmetic
    priority = db.Column(db.String(20), nullable=False) # Urgent, High, Medium, Low
    status = db.Column(db.String(30), nullable=False, default='New') # New, Assigned, In Progress, Resolved, Under Verification, Closed, Rejected, Reopened, Deferred
    
    location = db.Column(db.String(150), nullable=True) # E.g., Module / File name
    page_section = db.Column(db.String(100), nullable=True) # E.g., Page 14, Section 3.2
    
    reported_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    recommended_fix = db.Column(db.Text, nullable=True)
    reviewer_comments = db.Column(db.Text, nullable=True)
    developer_comments = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    attachment_path = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    comments = db.relationship('Comment', backref='defect', cascade='all, delete-orphan', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='defect', cascade='all, delete-orphan', lazy=True)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    defect_id = db.Column(db.Integer, db.ForeignKey('defects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='comments')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    defect_id = db.Column(db.Integer, db.ForeignKey('defects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False) # e.g., 'Created', 'Status Changed', 'Assigned', 'Comment Added'
    old_value = db.Column(db.String(255), nullable=True)
    new_value = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='activity_logs')


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False, default='info') # info, assignment, status_change, comment
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

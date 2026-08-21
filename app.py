import os
from flask import Flask, render_template, session, g
from config import Config
from models import db, User, Notification

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.projects import projects_bp
    from routes.documents import documents_bp
    from routes.inspections import inspections_bp
    from routes.defects import defects_bp
    from routes.reports import reports_bp
    from routes.analytics import analytics_bp
    from routes.team import team_bp
    from routes.settings import settings_bp
    from routes.help import help_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(inspections_bp)
    app.register_blueprint(defects_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_globals():
        user = None
        unread_count = 0
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                unread_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()

        return {
            'current_user': user,
            'unread_notifications_count': unread_count
        }

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    print("DesignInspect Server running at http://127.0.0.1:5050")
    app.run(debug=True, port=5050)


from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required, roles_required
from models import db, User, Category

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'profile':
            user.name = request.form.get('name', '').strip()
            user.email = request.form.get('email', '').strip().lower()
            password = request.form.get('password')

            if password:
                user.set_password(password)

            db.session.commit()
            session['user_name'] = user.name
            session['user_email'] = user.email

            flash('Profile updated successfully.', 'success')
            return redirect(url_for('settings.index'))

        elif action == 'add_category':
            cat_name = request.form.get('category_name', '').strip()
            cat_desc = request.form.get('category_desc', '').strip()

            if cat_name:
                if Category.query.filter_by(name=cat_name).first():
                    flash('Category already exists.', 'warning')
                else:
                    new_cat = Category(name=cat_name, description=cat_desc, is_custom=True)
                    db.session.add(new_cat)
                    db.session.commit()
                    flash(f'Custom defect category "{cat_name}" created.', 'success')
            return redirect(url_for('settings.index'))

    categories = Category.query.all()
    return render_template('settings/index.html', user=user, categories=categories)

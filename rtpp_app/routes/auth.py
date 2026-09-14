from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash
from rtpp_app.extensions import db, mail
from rtpp_app.models.user import User
from rtpp_app.forms import LoginForm, ForcePasswordChangeForm, ForgotPasswordForm, ResetPasswordForm

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect authenticated users to home
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    # Handle form submission
    if request.method == 'POST':
        # Validate required fields
        if not form.validate_on_submit():
            flash('Invalid email or password.', 'error')
            return render_template('login.html', form=form)

        # Attempt to authenticate user
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('You have been logged in.', 'success')

            # Redirect to force password change flow if required
            if user.must_change_pwd:
                return redirect(url_for('auth.force_password_change'))

            # Redirect to next or home
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))

        # Invalid credentials fallback
        flash('Invalid email or password.', 'error')

    # Render login form on GET or failed POST
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/force-password-change', methods=['GET', 'POST'])
@login_required
def force_password_change():
    # If password change is not required, redirect to home
    if not current_user.must_change_pwd:
        return redirect(url_for('home'))

    form = ForcePasswordChangeForm()
    if form.validate_on_submit():
        # Update password and clear flag
        current_user.set_password(form.password.data)
        current_user.must_change_pwd = False
        db.session.commit()

        flash('Your password has been changed. Please log in again.', 'success')
        logout_user()
        return redirect(url_for('auth.login'))

    return render_template('force_password_change.html', form=form)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def confirm_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except (SignatureExpired, BadSignature):
        return None
    return email

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)

            msg = Message("Password Reset Request", recipients=[user.email])
            msg.body = f'''
To reset your password, visit the following link:
{reset_url}
'''
            mail.send(msg)

        flash('If this email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))

    # Render forgot password form
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_reset_token(token)
    if not email:
        flash('Reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(form.password.data)
            db.session.commit()

            flash('Your password has been updated!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('User not found.', 'error')

    # Render reset password form
    return render_template('reset_password.html', form=form)

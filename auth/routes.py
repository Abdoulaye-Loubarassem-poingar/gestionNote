# auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt, limiter
from models import User
from .forms import LoginForm, RegisterForm
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Paramètres de verrouillage (tu peux ajuster depuis app config si tu préfères)
LOCK_THRESHOLD = 5         # essais max avant verrouillage
LOCK_SECONDS = 300        # verrouillage pendant 300s = 5 minutes

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # protection IP basique
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # Si utilisateur inexistant, ne pas renvoyer d'info ; on peut faire un dummy bcrypt pour égaliser le timing
        if not user:
            # dummy hash computation to mitigate timing attacks
            bcrypt.generate_password_hash("invalid_password")
            flash('❌ Email ou mot de passe incorrect.', 'danger')
            return redirect(url_for('auth.login'))

        # Vérifier si le compte est verrouillé
        if user.is_locked():
            remaining = int((user.locked_until - datetime.utcnow()).total_seconds())
            flash(f"Compte verrouillé temporairement. Réessayez dans {remaining} secondes.", 'warning')
            return redirect(url_for('auth.login'))

        # Vérifier mot de passe
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            # Succès : réinitialiser compteur et login
            user.reset_lock()
            db.session.commit()
            login_user(user, remember=form.remember.data)
            flash('✅ Connexion réussie !', 'success')
            return redirect(url_for('index'))
        else:
            # Échec : incrémenter compteur et éventuellement verrouiller
            user.register_failed_attempt(lock_threshold=LOCK_THRESHOLD, lock_seconds=LOCK_SECONDS)
            attempts_left = max(0, LOCK_THRESHOLD - user.failed_login_attempts)
            if user.is_locked():
                flash(f"Compte verrouillé après trop d'échecs. Réessayez dans {LOCK_SECONDS} secondes.", 'danger')
            else:
                flash(f"Identifiants invalides. Il vous reste {attempts_left} tentative(s).", 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    if form.validate_on_submit():
        # Vérifier doublon email
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash("Un compte avec cet email existe déjà.", "warning")
            return redirect(url_for('auth.register'))

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('✅ Compte créé, connectez-vous.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('auth.login'))

from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models import User
from extensions import db, bcrypt
from forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email déjà utilisé.")
            return redirect(url_for('auth.register'))
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Inscription réussie. Connectez-vous.")
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session.permanent = True
            flash("Connexion réussie.")
            return redirect(url_for('notes.dashboard'))
        flash("Identifiants invalides.")
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Déconnexion réussie.")
    return redirect(url_for('auth.login'))

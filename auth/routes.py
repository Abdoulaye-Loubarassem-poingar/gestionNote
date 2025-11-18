from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from extensions import db, bcrypt
from models import User
from auth.forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        # On cherche par username (comme ton formulaire)
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Connexion réussie !", "success")
            return redirect(url_for("notes.dashboard"))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_pw
        )

        db.session.add(user)
        db.session.commit()

        flash("Compte créé ! Connectez-vous.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Déconnecté.", "info")
    return redirect(url_for("auth.login"))

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from extensions import db, bcrypt
from models import User
from auth.forms import LoginForm, RegisterForm
from extensions import limiter
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username=form.username.data).first()

        if user:

            # Vérifier si le compte est bloqué
            if user.check_lock():
                flash(" Compte verrouillé pour 15 minutes après trop de tentatives.", "danger")
                return render_template("login.html", form=form)

            # Vérifier mot de passe
            if bcrypt.check_password_hash(user.password_hash, form.password.data):
                user.reset_attempts()
                login_user(user)
                flash("Connexion réussie ✔", "success")
                return redirect(url_for("notes.dashboard"))
            else:
                user.register_failure()
                remaining = User.MAX_ATTEMPTS - user.failed_attempts

                if remaining <= 0:
                    flash(" Trop de tentatives — compte bloqué 15 min.", "danger")
                else:
                    flash(f" Mot de passe incorrect — il reste {remaining} tentatives.", "danger")

        else:
            flash("Nom d’utilisateur incorrect.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash("⚠ Cet email existe déjà. Choisis un autre.", "danger")
            return render_template("register.html", form=form)

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_pw
        )

        db.session.add(user)
        db.session.commit()

        flash(" Compte créé avec succès !", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Déconnecté ✔", "info")
    return redirect(url_for("auth.login"))

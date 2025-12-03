from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required
from extensions import db, bcrypt, csrf
from models import User
from auth.forms import LoginForm, RegisterForm
from extensions import limiter
from sqlalchemy import or_

auth_bp = Blueprint("auth", __name__)

# ---------------------------------------------------
# 1️⃣ LOGIN NORMAL (formulaire HTML)
# ---------------------------------------------------
@limiter.limit("10 per minute")
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        identifier = form.username.data.strip()

        user = User.query.filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()

        if user:

            # Vérifier si compte verrouillé
            if user.check_lock():
                flash("Compte verrouillé pour 15 minutes.", "danger")
                return render_template("login.html", form=form)

            # Vérifier mot de passe
            if bcrypt.check_password_hash(user.password_hash, form.password.data):
                user.reset_attempts()
                login_user(user)
                flash("Connexion réussie ✔", "success")
                return redirect(url_for("notes.dashboard"))

            # Mot de passe incorrect
            user.register_failure()
            flash("Mot de passe incorrect.", "danger")
            return render_template("login.html", form=form)

        flash("Utilisateur introuvable.", "danger")

    return render_template("login.html", form=form)


# ---------------------------------------------------
# 2️⃣ ROUTE API SPÉCIALE POUR LES TESTS BRUTE-FORCE
# ---------------------------------------------------
@csrf.exempt
@limiter.limit("10 per minute")
@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    identifier = request.form.get("identifier", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter(
        or_(User.username == identifier, User.email == identifier)
    ).first()

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Vérifier verrouillage
    if user.check_lock():
        return jsonify({"status": "locked", "message": "Account locked"}), 403

    # Vérifier mot de passe
    if bcrypt.check_password_hash(user.password_hash, password):
        user.reset_attempts()
        return jsonify({"status": "success"}), 200

    # Tentative ratée
    user.register_failure()

    if user.is_locked:
        return jsonify({"status": "locked"}), 403

    return jsonify({"status": "error", "message": "Wrong password"}), 401


# ---------------------------------------------------
# 3️⃣ REGISTER (formulaire)
# ---------------------------------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            flash("Cet email est déjà utilisé.", "danger")
            return render_template("register.html", form=form)

        if User.query.filter_by(username=form.username.data).first():
            flash("Ce nom d'utilisateur existe déjà.", "danger")
            return render_template("register.html", form=form)

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_pw
        )

        db.session.add(user)
        db.session.commit()

        flash("Compte créé avec succès !", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


# ---------------------------------------------------
# 4️⃣ LOGOUT
# ---------------------------------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Déconnecté ✔", "info")
    return redirect(url_for("auth.login"))

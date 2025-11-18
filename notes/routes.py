from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, abort, current_app
)
from flask_login import login_required, current_user
from extensions import db
from models import Note, Tag
from auth.forms import NoteForm
from flask_wtf.csrf import validate_csrf
from sqlalchemy import or_
import os
import shutil
from datetime import datetime

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


# -------------------------
# Dashboard (liste des notes)
# -------------------------
@notes_bp.route("/dashboard")
@login_required
def dashboard():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "")
    tag_filter = request.args.get("tag", "")

    per_page = 6
    notes_query = Note.query.filter_by(user_id=current_user.id)

    # Recherche texte
    if q:
        notes_query = notes_query.filter(
            or_(Note.title.contains(q), Note.content.contains(q))
        )

    # Filtre tag
    if tag_filter:
        notes_query = notes_query.join(Note.tags).filter(Tag.name == tag_filter)

    pagination = notes_query.order_by(Note.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    notes = pagination.items
    last_page = pagination.pages if pagination.pages else 1

    # Tous les tags de l’utilisateur
    all_notes = Note.query.filter_by(user_id=current_user.id).all()
    user_tags = sorted({t.name for n in all_notes for t in n.tags})

    return render_template(
        "note.html",
        notes=notes,
        q=q,
        tag_filter=tag_filter,
        user_tags=user_tags,
        page=page,
        last_page=last_page
    )


# -------------------------
# Ajouter une note
# -------------------------
@notes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_note():
    form = NoteForm()

    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )

        # Tags
        tags_list = [t.strip() for t in (form.tags.data or "").split(",") if t.strip()]
        for name in tags_list:
            tag = Tag.query.filter_by(name=name).first() or Tag(name=name)
            note.tags.append(tag)

        db.session.add(note)
        db.session.commit()
        flash("Note ajoutée !", "success")
        return redirect(url_for("notes.dashboard"))

    return render_template("add_note.html", form=form)


# -------------------------
# Modifier note
# -------------------------
@notes_bp.route("/edit/<int:note_id>", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)

    if note.user_id != current_user.id:
        abort(403)

    form = NoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        note.tags.clear()
        tags_list = [t.strip() for t in (form.tags.data or "").split(",") if t.strip()]
        for name in tags_list:
            tag = Tag.query.filter_by(name=name).first() or Tag(name=name)
            note.tags.append(tag)

        db.session.commit()
        flash("Note mise à jour !", "success")
        return redirect(url_for("notes.dashboard"))

    form.tags.data = ", ".join([t.name for t in note.tags])
    return render_template("edit_note.html", form=form)


# -------------------------
# Supprimer une note
# -------------------------
@notes_bp.route("/delete/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    try:
        validate_csrf(request.form.get("csrf_token"))
    except:
        abort(400, description="CSRF token missing or invalid.")

    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403)

    db.session.delete(note)
    db.session.commit()

    flash("Note supprimée.", "success")
    return redirect(url_for("notes.dashboard"))


# -------------------------
# Export HTML
# -------------------------
@notes_bp.route("/export")
@login_required
def export_pdf():
    q = request.args.get("q", "")
    tag = request.args.get("tag", "")

    notes_query = Note.query.filter_by(user_id=current_user.id)

    if q:
        notes_query = notes_query.filter(
            or_(Note.title.contains(q), Note.content.contains(q))
        )

    if tag:
        notes_query = notes_query.join(Note.tags).filter(Tag.name == tag)

    notes = notes_query.order_by(Note.created_at.desc()).all()

    return render_template("export_pdf.html", notes=notes)


# -------------------------
# Backup DB
# -------------------------
@notes_bp.route("/backup")
@login_required
def backup_db():
    uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///"):
        db_path = uri.replace("sqlite:///", "")
    else:
        db_path = os.path.join(current_app.instance_path, "app.db")

    if not os.path.exists(db_path):
        flash("Base de données introuvable.", "danger")
        return redirect(url_for("notes.dashboard"))

    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join(current_app.instance_path, backup_name)

    try:
        shutil.copy(db_path, backup_path)
        flash(f"Sauvegarde créée : {backup_name}", "success")
    except Exception as e:
        flash(f"Erreur : {e}", "danger")

    return redirect(url_for("notes.dashboard"))

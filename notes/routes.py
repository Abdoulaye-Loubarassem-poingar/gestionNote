# notes/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Note
from auth.forms import NoteForm

notes_bp = Blueprint('notes', __name__, url_prefix='/notes')

@notes_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(note)
        db.session.commit()
        flash('✅ Note ajoutée !', 'success')
        return redirect(url_for('notes.view_notes'))
    return render_template('add_note.html', form=form)

@notes_bp.route('/')
@login_required
def view_notes():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('notes.html', notes=notes)

@notes_bp.route('/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("❌ Pas la permission de modifier cette note.", 'danger')
        return redirect(url_for('notes.view_notes'))

    form = NoteForm()
    if request.method == 'GET':
        form.title.data = note.title
        form.content.data = note.content

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()
        flash("✅ Note modifiée !", 'success')
        return redirect(url_for('notes.view_notes'))

    return render_template('edit_note.html', form=form, note=note)

@notes_bp.route('/delete/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("❌ Pas la permission de supprimer cette note.", 'danger')
        return redirect(url_for('notes.view_notes'))

    db.session.delete(note)
    db.session.commit()
    flash("🗑️ Note supprimée.", 'info')
    return redirect(url_for('notes.view_notes'))

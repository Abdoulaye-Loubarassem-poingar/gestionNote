from flask import Blueprint, render_template, redirect, url_for, flash, session
from models import Note
from extensions import db
from forms import NoteForm
from functools import wraps

notes_bp = Blueprint('notes', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Connectez-vous pour accéder à cette page.")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@notes_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    notes = Note.query.filter_by(user_id=user_id).all()
    return render_template('notes.html', notes=notes)

@notes_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_note():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(title=form.title.data, content=form.content.data, user_id=session['user_id'])
        db.session.add(note)
        db.session.commit()
        flash("Note ajoutée.")
        return redirect(url_for('notes.dashboard'))
    return render_template('add_note.html', form=form)

@notes_bp.route('/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != session['user_id']:
        flash("Accès refusé.")
        return redirect(url_for('notes.dashboard'))
    form = NoteForm(obj=note)
    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        db.session.commit()
        flash("Note modifiée.")
        return redirect(url_for('notes.dashboard'))
    return render_template('add_note.html', form=form)

@notes_bp.route('/delete/<int:note_id>')
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != session['user_id']:
        flash("Accès refusé.")
        return redirect(url_for('notes.dashboard'))
    db.session.delete(note)
    db.session.commit()
    flash("Note supprimée.")
    return redirect(url_for('notes.dashboard'))

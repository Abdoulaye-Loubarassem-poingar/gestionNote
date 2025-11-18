# models.py
from datetime import datetime
import secrets
from extensions import db
from flask_login import UserMixin

note_tag = db.Table(
    'note_tag',
    db.Column('note_id', db.Integer, db.ForeignKey('note.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    api_token = db.Column(db.String(64), unique=True, index=True, nullable=True)

    notes = db.relationship("Note", backref="owner", lazy="dynamic")
    reminders = db.relationship("Reminder", back_populates="user", lazy="dynamic")

    def generate_api_token(self):
        token = secrets.token_hex(32)
        self.api_token = token
        db.session.add(self)
        db.session.commit()
        return token

    def revoke_api_token(self):
        self.api_token = None
        db.session.commit()

class Note(db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.relationship('Tag', secondary=note_tag, back_populates='notes')

class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    notes = db.relationship('Note', secondary=note_tag, back_populates='tags')

class Reminder(db.Model):
    __tablename__ = "reminder"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=True)
    remind_at = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="reminders")
    note = db.relationship("Note")

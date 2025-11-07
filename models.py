# models.py
from extensions import db
from flask_login import UserMixin
from datetime import datetime, timedelta

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True)

    # --- champs pour verrouillage / anti-brute-force ---
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    last_failed_login_at = db.Column(db.DateTime, nullable=True)
    locked_until = db.Column(db.DateTime, nullable=True)

    def is_locked(self):
        """Retourne True si le compte est temporairement verrouillé."""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False

    def reset_lock(self):
        self.failed_login_attempts = 0
        self.last_failed_login_at = None
        self.locked_until = None

    def register_failed_attempt(self, lock_threshold=5, lock_seconds=300):
        """Incrémente le compteur et verrouille si seuil atteint.
        lock_threshold: nombre d'essais max avant verrouillage
        lock_seconds: durée du verrouillage en secondes
        """
        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1
        self.last_failed_login_at = datetime.utcnow()
        if self.failed_login_attempts >= lock_threshold:
            self.locked_until = datetime.utcnow() + timedelta(seconds=lock_seconds)
        db.session.add(self)
        db.session.commit()


class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

from extensions import db
from datetime import datetime, timedelta
from flask_login import UserMixin
import secrets


# TABLE D’ASSOCIATION NOTE <-> TAG

note_tag = db.Table(
    "note_tag",
    db.Column("note_id", db.Integer, db.ForeignKey("note.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


# USER MODEL (SÉCURITÉ + FLASK-LOGIN + ANTI BRUTE-FORCE)

class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    #  Bruteforce protection
    failed_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    is_locked = db.Column(db.Boolean, default=False)

    # RÈGLES
    LOCK_TIME = 15        # minutes
    MAX_ATTEMPTS = 10     # max tries before lock

    #  FLASK-LOGIN required methods 
    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True   # Tous les comptes sont actifs

    #  Bruteforce functions 
    def check_lock(self):
        """Retourne True si le compte est encore bloqué."""
        if not self.is_locked:
            return False

        # Check si le délai est expiré
        if self.last_failed_login and \
           datetime.utcnow() > self.last_failed_login + timedelta(minutes=self.LOCK_TIME):

            # Débloquer
            self.is_locked = False
            self.failed_attempts = 0
            db.session.commit()
            return False

        return True

    def register_failure(self):
        """Ajoute une tentative échouée."""
        self.failed_attempts += 1
        self.last_failed_login = datetime.utcnow()

        if self.failed_attempts >= self.MAX_ATTEMPTS:
            self.is_locked = True

        db.session.commit()

    def reset_attempts(self):
        """Reset après une connexion réussie."""
        self.failed_attempts = 0
        self.is_locked = False
        db.session.commit()



# TAG MODEL

class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)



# CATEGORY MODEL (OPTIONNEL)

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    notes = db.relationship("Note", backref="category", lazy="dynamic")



# NOTE MODEL (TAGS + CATEGORIES + IMPORTANT/PIN)

class Note(db.Model):
    __tablename__ = "note"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Flags
    is_important = db.Column(db.Boolean, default=False, nullable=False)
    pinned = db.Column(db.Boolean, default=False, nullable=False)

    # FK vers catégorie
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)

    # Tags many-to-many
    tags = db.relationship(
        "Tag",
        secondary=note_tag,
        backref=db.backref("notes", lazy="dynamic")
    )

# models.py
from extensions import db
from datetime import datetime, timedelta
from flask_login import UserMixin

# Table d'association Note <-> Tag
note_tag = db.Table(
    "note_tag",
    db.Column("note_id", db.Integer, db.ForeignKey("note.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # Brute-force protection
    failed_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    is_locked = db.Column(db.Boolean, default=False)

    MAX_ATTEMPTS = 10
    LOCK_TIME = 15  # minutes

    def check_lock(self):
        """Check if user is locked after too many failed logins."""
        if not self.is_locked:
            return False

        unlock_time = self.last_failed_login + timedelta(minutes=self.LOCK_TIME)
        if datetime.utcnow() >= unlock_time:
            self.is_locked = False
            self.failed_attempts = 0
            db.session.commit()
            return False

        return True

    def register_failure(self):
        """Count a failed attempt."""
        self.failed_attempts += 1
        self.last_failed_login = datetime.utcnow()

        if self.failed_attempts >= self.MAX_ATTEMPTS:
            self.is_locked = True

        db.session.commit()

    def reset_attempts(self):
        """Reset counters after success."""
        self.failed_attempts = 0
        self.is_locked = False
        db.session.commit()


class Tag(db.Model):
    __tablename__ = "tag"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    # Relation optionnelle
    notes = db.relationship("Note", backref="category", lazy="dynamic")


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

    # Category
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)

    # Tags many-to-many
    tags = db.relationship(
        "Tag",
        secondary=note_tag,
        backref=db.backref("notes", lazy="dynamic")
    )

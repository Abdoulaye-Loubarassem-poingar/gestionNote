from datetime import datetime
from extensions import db
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
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    api_token = db.Column(db.String(255), nullable=True)

    notes = db.relationship("Note", backref="owner", lazy="dynamic")

class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    # Optionnel: relation reverse
    notes = db.relationship("Note", backref="category", lazy="dynamic")

class Note(db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # flags
    is_important = db.Column(db.Boolean, default=False, nullable=False)
    pinned = db.Column(db.Boolean, default=False, nullable=False)

    # category FK (nullable)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)

    # tags many-to-many
    tags = db.relationship("Tag", secondary=note_tag, backref=db.backref("notes", lazy="dynamic"))

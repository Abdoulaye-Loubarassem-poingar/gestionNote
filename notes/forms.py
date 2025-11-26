from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional


class NoteForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired()])
    content = TextAreaField("Contenu", validators=[DataRequired()])
    tags = StringField("Tags (séparés par des virgules)", validators=[Optional()])
    is_important = BooleanField("Important")
    pinned = BooleanField("Epingle")
    category = StringField("Catégorie (ex: travail, perso)", validators=[Optional()])
    submit = SubmitField("Enregistrer")

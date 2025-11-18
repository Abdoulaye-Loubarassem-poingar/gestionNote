from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")


class RegisterForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Créer un compte")


class NoteForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired(), Length(max=150)])
    content = TextAreaField("Contenu", validators=[DataRequired()])
    tags = StringField("Tags (séparés par des virgules)", validators=[Length(max=200)])
    submit = SubmitField("Enregistrer")

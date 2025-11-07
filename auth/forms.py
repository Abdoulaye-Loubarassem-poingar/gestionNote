# auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Se connecter')


class RegisterForm(FlaskForm):
    username = StringField('Nom d’utilisateur', validators=[DataRequired(), Length(min=3, max=25)])
    email = EmailField('Adresse e-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
    submit = SubmitField("S'inscrire")

class NoteForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(), Length(min=1, max=100)])
    content = TextAreaField('Contenu', validators=[DataRequired()])
    submit = SubmitField('Ajouter une note')


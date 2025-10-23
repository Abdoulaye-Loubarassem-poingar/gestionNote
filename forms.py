from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, Regexp

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$',
               message="Le mot de passe doit contenir majuscule, minuscule, chiffre et caractère spécial")
    ])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])

class NoteForm(FlaskForm):
    title = StringField('Titre', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Contenu', validators=[DataRequired()])

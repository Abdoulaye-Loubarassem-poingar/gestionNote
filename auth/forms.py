from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo
from models import User
import re

class RegisterForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired(), Length(min=3, max=30)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Créer un compte")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Cet email est déjà utilisé. Essaie un autre.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Ce nom d'utilisateur existe déjà.")

    def validate_password(self, field):
        pwd = field.data or ""
        if (len(pwd) < 8
            or not re.search(r"[A-Z]", pwd)
            or not re.search(r"[0-9]", pwd)
            or not re.search(r"[\W_]", pwd)
        ):
            raise ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères, "
                "une lettre majuscule, un chiffre et un caractère spécial."
            )

class LoginForm(FlaskForm):
    # identifier permet username ou email
    identifier = StringField("Nom d'utilisateur ou Email", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Connexion")

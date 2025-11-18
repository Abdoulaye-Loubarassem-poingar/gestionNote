# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_talisman import Talisman

db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
mail = Mail()
login_manager = LoginManager()
limiter = Limiter(key_func=lambda: "global")  # for dev. Configure properly for prod
talisman = Talisman()

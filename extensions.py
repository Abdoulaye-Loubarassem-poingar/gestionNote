# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman

db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
# Talisman will be initialized in app factory with CSP settings
talisman = Talisman()

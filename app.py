# app.py
import os
from flask import Flask, render_template
from extensions import db, bcrypt, csrf, login_manager, limiter, talisman
from auth.routes import auth_bp
from notes.routes import notes_bp
from models import User
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import logging



load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

   
    # SECURITY / CONFIG
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_me_long_random')

    # DATABASE
    instance_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance")
    os.makedirs(instance_dir, exist_ok=True)
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance", "app.db")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # CSRF
    app.config["WTF_CSRF_ENABLED"] = True

    # Cookies sécurisés
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,        # mettre True uniquement avec HTTPS
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SECURE=False
    )

    
    # EXTENSIONS
   
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Flask-Login
    limiter.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

   
    # TALISMAN (CSP assoupli pour Bootstrap / JS)
    
    csp = {
        'default-src': ["'self'"],
        'img-src': ["'self'", "data:"],
        'style-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        'script-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        'font-src': ["'self'", "https://cdn.jsdelivr.net"],
    }

    talisman.init_app(
        app,
        content_security_policy=csp,
        force_https=False  # mettre True seulement en production
    )

    # Fix reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    
    # BLUEPRINTS
   
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)

    
    # ROUTES
    
    @app.route('/')
    def index():
        return render_template('index.html')

   
    # ERROR HANDLERS
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception("500 Internal Server Error: %s", e)
        return render_template('500.html'), 500

    
    # LOGGING
    
    handler = logging.FileHandler('app.log', encoding='utf-8')
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    return app



# RUN APP

if __name__ == "__main__":
    app = create_app()

    # Assurer que le dossier instance existe
    os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance"), exist_ok=True)

    # Créer DB si manquante
    with app.app_context():
        db.create_all()

    app.run(debug=True)

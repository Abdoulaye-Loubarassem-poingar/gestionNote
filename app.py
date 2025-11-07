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

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_me_long_random')
    # DB path absolute to avoid path issues
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance", "app.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"sqlite:///{db_path}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Session / cookies hardening
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,   # en dev local laisser False; mettre True en prod avec HTTPS
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SECURE=False,  # idem
        SESSION_COOKIE_SAMESITE='Lax',
    )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    # Flask-Login configuration and user loader
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Talisman / security headers (force_https=False in dev)
    csp = {
        'default-src': ["'self'"],
        'script-src': ["'self'"],
        'style-src': ["'self'"],
    }
    talisman.init_app(
        app,
        content_security_policy=csp,
        force_https=False,  # mettre True en prod + SESSION_COOKIE_SECURE True
    )

    # Proxy fix if behind reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)

    # Simple index route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Error handlers
    @app.errorhandler(500)
    def internal_error(e):
        app.logger.exception("Server error: %s", e)
        return render_template('500.html'), 500

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    # Logging to file
    handler = logging.FileHandler('app.log', encoding='utf-8')
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    return app

if __name__ == "__main__":
    app = create_app()

    # ensure instance folder exists
    os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), "instance"), exist_ok=True)

    # create DB
    with app.app_context():
        db.create_all()

    # Run app (debug True in dev)
    app.run(host="127.0.0.1", port=5000, debug=True)

from flask import Flask, render_template
from extensions import db, bcrypt
from auth.routes import auth_bp
from notes.routes import notes_bp
import os
from datetime import timedelta

app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'un_secret_long_et_unique'

# Chemin absolu pour la DB
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'notes.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Expiration de session
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Initialiser extensions
db.init_app(app)
bcrypt.init_app(app)

# Enregistrer les Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp)

# Création DB
with app.app_context():
    db.create_all()

# En-têtes sécurité
@app.after_request
def set_secure_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' https://cdn.jsdelivr.net"
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

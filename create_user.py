from app import create_app
from models import User
from extensions import db

app = create_app()
with app.app_context():
    u = User(username='admin')
    u.set_password('password123')
    db.session.add(u)
    db.session.commit()
    print("✅ Utilisateur créé :", u.username)

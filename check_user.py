# check_user.py
from app import create_app
from models import User
from extensions import db

app = create_app()

with app.app_context():
    users = User.query.all()
    
    if not users:
        print("Aucun utilisateur trouvé.")
    else:
        print("\n===== UTILISATEURS TROUVÉS =====\n")
        for u in users:
            print(f"ID: {u.id} | Username: {u.username} | Email: {u.email} | Password Hash: {u.password_hash}")

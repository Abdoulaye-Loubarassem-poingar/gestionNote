from app import create_app
from models import User
from extensions import db

app = create_app()
with app.app_context():
    user = User.query.first()
    if user:
        print("Utilisateur trouvé :", user.username)
        print("Hash du mot de passe :", user.password_hash)
    else:
        print("Aucun utilisateur trouvé dans la base.")

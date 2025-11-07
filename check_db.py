# check_db.py
from app import create_app
from extensions import db
from models import User, Note

def audit_db():
    app = create_app()
    with app.app_context():
        print("=== AUDIT BASE DE DONNÉES ===\n")
        try:
            users = User.query.all()
            print(f"Utilisateurs : {len(users)}")
            for u in users:
                print(f"- ID {u.id} | username: {u.username} | email: {u.email}")
                print(f"  password_hash: {u.password_hash[:30]}...")
                notes = Note.query.filter_by(user_id=u.id).all()
                print(f"  notes: {len(notes)}")
                for n in notes:
                    print(f"    * ({n.id}) {n.title} -> {n.content[:40]}...")
            print("\n=== Fin audit ===")
        except Exception as e:
            print("Erreur audit:", e)

if __name__ == "__main__":
    audit_db()

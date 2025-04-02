from models.userModel import User
from extensions import db 

def create_user(email, password_hash, name):
    try:
        new_user = User(
            Email=email,
            FullName=name,
            PasswordHash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Erro ao salvar o usuário: {str(e)}")

def get_user_by_email(email):
    return User.query.filter_by(Email=email).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)
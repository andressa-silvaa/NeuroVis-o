from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

# Função para criar um novo usuário
def create_user(email, password, name):
    hashed_password = generate_password_hash(password)  # Criptografando a senha
    new_user = User(email=email, password=hashed_password, name=name)

    try:
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Erro ao salvar o usuário: {str(e)}")

# Função para buscar um usuário pelo email
def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

# Função para buscar um usuário pelo ID
def get_user_by_id(user_id):
    return User.query.get(user_id)

# # Função para atualizar o perfil de um usuário
# def update_user(user, name, email):
#     user.name = name
#     user.email = email

#     try:
#         db.session.commit()
#         return user
#     except Exception as e:
#         db.session.rollback()
#         raise Exception(f"Erro ao atualizar o usuário: {str(e)}")

from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token
from models import User, db  # Importando User e db para interagir com a base de dados
from repositories import create_user, get_user_by_email, get_user_by_id, update_user

# Função para registrar um usuário
def register_user(data):
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    # Verifica se o email já está cadastrado
    existing_user = get_user_by_email(email)
    if existing_user:
        raise ValidationError("Email já cadastrado.")

    # Criptografa a senha
    hashed_password = generate_password_hash(password)

    # Chama o repositório para criar o novo usuário
    user = create_user(email, hashed_password, name)
    return user

# Função para realizar o login do usuário
def login_user(email, password):
    # Verifica se o email está registrado
    user = get_user_by_email(email)
    if not user:
        raise ValidationError("Usuário não encontrado.")

    # Verifica se a senha está correta
    if not check_password_hash(user.password, password):
        raise ValidationError("Senha incorreta.")

    # Cria o token de acesso (JWT)
    access_token = create_access_token(identity=user.id)
    return {"access_token": access_token}

# Função para atualizar o perfil de um usuário
def update_user_profile(user_id, data):
    # Busca o usuário pelo ID
    user = get_user_by_id(user_id)
    if not user:
        raise ValidationError("Usuário não encontrado.")

    # Atualiza os dados do usuário
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)

    # Chama o repositório para atualizar o usuário
    updated_user = update_user(user)
    return updated_user

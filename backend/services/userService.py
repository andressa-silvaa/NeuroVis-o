from werkzeug.security import generate_password_hash
from marshmallow import ValidationError
from models.userModel import User
from schemas.UserRegistrationSchema import UserRegistrationSchema
from schemas.userLoginSchema import UserLoginSchema
from repositories.userRepository import create_user, get_user_by_email
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token  
)

def validate_registration_data(data):
    schema = UserRegistrationSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return schema.load(data)

def validate_login_data(data):
    schema = UserLoginSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return schema.load(data) 

def register_user(data):
    try:
        validated_data = validate_registration_data(data)
        
        email = validated_data['email']
        password = validated_data['password']
        name = validated_data['name']

        existing_user = get_user_by_email(email)
        if existing_user:
            raise ValidationError({"email": ["Email já cadastrado"]})

        hashed_password = generate_password_hash(password)
        user = create_user(email, hashed_password, name)
        return user

    except ValidationError as e:
        raise e  
    except Exception as e:
        raise Exception(f"Erro ao criar usuário: {str(e)}")

def login_user(email, password):
    try:
        validated_data = validate_login_data({'email': email, 'password': password})
        email = validated_data['email']
        password = validated_data['password']

        user = get_user_by_email(email)
        if not user:
            raise ValidationError({"email": ["Credenciais inválidas"]})

        if not user.check_password(password):
            raise ValidationError({"password": ["Credenciais inválidas"]})

        access_token = create_access_token(identity=str(user.UserID)) 
        refresh_token = create_refresh_token(identity=str(user.UserID))

        return (user, access_token, refresh_token) 

    except ValidationError as e:
        raise e
    except Exception as e:
        raise Exception(f"Erro durante o login: {str(e)}")

from flask import Blueprint, request, jsonify
from services.userService import register_user, login_user
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user = register_user(data)
        return jsonify({
            "message": "Usuário criado com sucesso",
            "user": {
                "id": user.UserID,
                "name": user.FullName,
                "email": user.Email
            }
        }), 201
        
    except ValidationError as e:
        return jsonify({
            "error": "Erro de validação",
            "details": e.messages  
        }), 400
        
    except Exception as e:
        return jsonify({
            "error": "Erro ao criar usuário",
            "message": str(e)
        }), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        user, access_token = login_user(data.get('email'), data.get('password'))
        
        return jsonify({
            "message": "Login bem-sucedido",
            "access_token": access_token,
            "user": {
                "id": user.UserID,
                "name": user.FullName,
                "email": user.Email
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({
            "error": "Erro de autenticação",
            "details": e.messages  
        }), 401
        
    except Exception as e:
        return jsonify({
            "error": "Erro ao realizar login",
            "message": str(e)
        }), 500
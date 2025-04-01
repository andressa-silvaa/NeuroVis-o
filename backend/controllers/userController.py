from flask import Blueprint, request, jsonify
from services.userService import register_user, login_user, update_user_profile
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Cria o Blueprint para o userController
user_bp = Blueprint('user', __name__)

# Rota de Registro de Usuário
@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        user = register_user(data)  # Chama o serviço para registrar o usuário
        return jsonify({"message": "Usuário criado com sucesso", "user": user.name}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro ao criar usuário", "message": str(e)}), 500

# Rota de Login de Usuário
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        user = login_user(email, password)  # Chama o serviço para realizar o login
        # Cria o token JWT
        access_token = create_access_token(identity=user.id)
        return jsonify({"message": "Login bem-sucedido", "token": access_token}), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Erro ao realizar login", "message": str(e)}), 500

# Rota de Atualização de Perfil de Usuário (necessita de autenticação)
# @user_bp.route('/profile', methods=['PUT'])
# @jwt_required()  # Garante que o usuário está autenticado
# def update_profile():
#     current_user_id = get_jwt_identity()  # Pega o ID do usuário logado
#     data = request.get_json()

#     try:
#         updated_user = update_user_profile(current_user_id, data)  # Chama o serviço para atualizar o perfil
#         return jsonify({"message": "Perfil atualizado com sucesso", "user": updated_user.name}), 200
#     except ValidationError as e:
#         return jsonify({"error": str(e)}), 400
#     except Exception as e:
#         return jsonify({"error": "Erro ao atualizar perfil", "message": str(e)}), 500

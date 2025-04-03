from flask import Flask, jsonify
from config.config import Config
from extensions import db
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt = JWTManager(app)
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error": "token_expired",
            "message": "O token de acesso expirou"
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            "error": "invalid_token",
            "message": "Token de acesso inválido"
        }), 401

    # Registra blueprints
    with app.app_context():
        from controllers.userController import user_bp
        from controllers.neuralNetworkController import neural_bp
        
        app.register_blueprint(user_bp)
        app.register_blueprint(neural_bp)
        
        # Cria tabelas do banco de dados
        from models.userModel import User
        from models.imageModel import Image, ObjectRecognitionResult
        from models.ObjectRecognitionResultModel import ObjectRecognitionResult
        db.create_all()
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
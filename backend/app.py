from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config.config import Config
from extensions import db, jwt 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializa extensões
    db.init_app(app)
    jwt.init_app(app)
    
    # Importa e registra blueprints DENTRO da função create_app
    from controllers.userController import user_bp
    app.register_blueprint(user_bp)
    
    return app

app = create_app()

# Import dos models deve vir DEPOIS de criar o app
from models.userModel import User

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
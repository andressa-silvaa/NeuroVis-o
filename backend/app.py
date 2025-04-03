from flask import Flask, jsonify
from config.config import Config
from extensions import db
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    jwt = JWTManager(app)
    
    with app.app_context():
        from controllers.userController import user_bp
        app.register_blueprint(user_bp)
        
        from models.userModel import User
        db.create_all()
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
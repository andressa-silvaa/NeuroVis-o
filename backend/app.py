from flask import Flask, jsonify
from config.config import Config
from extensions import db
from flask_jwt_extended import JWTManager
import logging
from datetime import datetime

def configure_logging():
    """Configuração centralizada de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
    return logging.getLogger(__name__)

def create_app():
    """Factory principal da aplicação Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    logger = configure_logging()
    
    try:
        db.init_app(app)
        jwt = JWTManager(app)
        logger.info("Extensões inicializadas com sucesso")
    except Exception as e:
        logger.critical(f"Falha na inicialização de extensões: {str(e)}")
        raise

    configure_jwt_handlers(jwt, logger)

    with app.app_context():
        register_blueprints(app, logger)
        initialize_database(app, db, logger)

    register_utility_endpoints(app, db, logger)

    return app

def configure_jwt_handlers(jwt, logger):
    """Configura os handlers de erro do JWT"""
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"Token expirado tentou acessar: {jwt_payload}")
        return jsonify({
            "status": "error",
            "message": "Token expirado",
            "code": 401
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"Token inválido recebido: {str(error)}")
        return jsonify({
            "status": "error",
            "message": "Token de acesso inválido ou malformado",
            "code": 401
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.warning("Tentativa de acesso não autorizado")
        return jsonify({
            "status": "error",
            "message": "Token de acesso não fornecido",
            "code": 401
        }), 401

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return False

def register_blueprints(app, logger):
    """Registra todos os blueprints da aplicação"""
    try:
        from controllers.userController import user_bp
        from controllers.neuralNetworkController import neural_bp
        
        app.register_blueprint(user_bp)
        app.register_blueprint(neural_bp)
        logger.info("Blueprints registrados com sucesso")
    except Exception as e:
        logger.error(f"Falha ao registrar blueprints: {str(e)}")
        raise

def initialize_database(app, db, logger):
    """Inicializa e verifica o banco de dados"""
    try:
        from models.userModel import User
        from models.imageModel import Image
        from models.ObjectRecognitionResultModel import ObjectRecognitionResult
        
        db.create_all()
        logger.info("Tabelas do banco de dados verificadas/criadas")
    except Exception as e:
        logger.critical(f"Falha na inicialização do banco de dados: {str(e)}")
        raise

def register_utility_endpoints(app, db, logger):
    """Registra endpoints utilitários"""
    @app.route('/health')
    def health_check():
        """Endpoint de verificação de saúde da aplicação"""
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": test_database_connection(db),
                "authentication": "active"
            }
        }
        logger.debug("Health check realizado")
        return jsonify(status)

    @app.route('/version')
    def version():
        """Endpoint de versão da aplicação"""
        return jsonify({
            "name": "NeuroVision API",
            "version": "1.0.0",
            "environment": Config.ENVIRONMENT
        })

def test_database_connection(db):
    """Testa a conexão com o banco de dados"""
    try:
        db.session.execute("SELECT 1")
        return "connected"
    except Exception:
        return "disconnected"

app = create_app()

if __name__ == "__main__":
    app.run(
        host=Config.APP_HOST,
        port=Config.APP_PORT,
        debug=Config.DEBUG_MODE,
        threaded=True
    )
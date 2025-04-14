import os
from flask import Flask, jsonify
from config.config import Config, ProductionConfig
from extensions import db
from flask_jwt_extended import JWTManager
import logging
from datetime import datetime
from flask_cors import CORS
from sqlalchemy import text

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
    return logging.getLogger(__name__)

def get_allowed_origins():
    allowed_origins = os.environ.get('ALLOWED_ORIGINS')
    if allowed_origins:
        return [origin.strip() for origin in allowed_origins.split(',')]
    return ["http://localhost:4200"]

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    config_class.init_app(app)

    # ✅ CORS com origens seguras e explícitas
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {"origins": get_allowed_origins()}
    })

    logger = configure_logging()
    logger.info(f"Iniciando aplicação no ambiente: {config_class.__name__}")
    logger.info(f"CORS habilitado para: {get_allowed_origins()}")

    try:
        db.init_app(app)
        jwt = JWTManager(app)
        logger.info("Extensões inicializadas com sucesso")
    except Exception as e:
        logger.critical(f"Falha na inicialização de extensões: {str(e)}", exc_info=True)
        raise

    configure_jwt_handlers(jwt, logger)

    with app.app_context():
        try:
            register_blueprints(app, logger)
            initialize_database(app, db, logger)
        except Exception as e:
            logger.critical(f"Falha na inicialização da aplicação: {str(e)}", exc_info=True)
            raise

    register_utility_endpoints(app, db, logger)

    return app

def configure_jwt_handlers(jwt, logger):
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"Token expirado tentou acessar: {jwt_payload}")
        return jsonify({"status": "error", "message": "Token expirado", "code": 401}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"Token inválido recebido: {str(error)}")
        return jsonify({"status": "error", "message": "Token inválido ou malformado", "code": 401}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.warning("Tentativa de acesso não autorizado")
        return jsonify({"status": "error", "message": "Token não fornecido", "code": 401}), 401

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return False

def register_blueprints(app, logger):
    try:
        from controllers.userController import user_bp
        from controllers.neuralNetworkController import neural_bp

        app.register_blueprint(user_bp, url_prefix='/api/users')
        app.register_blueprint(neural_bp, url_prefix='/api/neural')
        logger.info("Blueprints registrados com sucesso")
    except ImportError as e:
        logger.error(f"Erro ao importar blueprints: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar blueprints: {str(e)}", exc_info=True)
        raise

def initialize_database(app, db, logger):
    try:
        from models.userModel import User
        from models.imageModel import Image
        from models.ObjectRecognitionResultModel import ObjectRecognitionResult

        db.create_all()
        logger.info("Tabelas verificadas/criadas")

        db.session.execute(text("SELECT 1"))
        logger.info("Conexão com o banco de dados OK")
    except Exception as e:
        logger.critical(f"Erro na inicialização do banco: {str(e)}", exc_info=True)
        raise

def register_utility_endpoints(app, db, logger):
    @app.route('/health')
    def health_check():
        status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": test_database_connection(db),
                "authentication": "active"
            },
            "environment": app.config.get("ENV", "production")
        }
        logger.debug("Health check realizado")
        return jsonify(status)

    @app.route('/version')
    def version():
        return jsonify({
            "name": "NeuroVision API",
            "version": "1.0.0",
            "environment": app.config.get("ENV", "production")
        })

def test_database_connection(db):
    try:
        db.session.execute(text("SELECT 1"))
        return "connected"
    except Exception as e:
        return f"disconnected: {str(e)}"

# Início da aplicação
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('DEBUG_MODE', 'False').lower() == 'true',
        threaded=True
    )

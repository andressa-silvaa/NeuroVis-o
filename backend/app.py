import os
from flask import Flask, jsonify, send_from_directory
from config.config import Config, ProductionConfig
from extensions import db
from flask_jwt_extended import JWTManager
import logging
from datetime import datetime
from flask_cors import CORS
from sqlalchemy import text
from pathlib import Path

def configure_logging():
    """Configuração avançada de logging com rotação de arquivos"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', encoding='utf-8')
        ]
    )
    
    # Configuração adicional para logs do SQLAlchemy
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def get_allowed_origins():
    """Obtém origens permitidas para CORS com validação"""
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', '').strip()
    if allowed_origins:
        origins = [origin.strip() for origin in allowed_origins.split(',') if origin.strip()]
        if origins:
            return origins
    
    # Fallback para desenvolvimento
    return ["http://localhost:4200", "http://127.0.0.1:4200"]

def create_app(config_class=ProductionConfig):
    """Factory de aplicação Flask com configuração robusta"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configuração inicial
    config_class.init_app(app)
    logger = configure_logging()
    
    try:
        # ✅ CORS seguro com origens validadas
        cors_origins = get_allowed_origins()
        CORS(app, 
             supports_credentials=True, 
             resources={r"/api/*": {"origins": cors_origins}},
             expose_headers=["Content-Disposition"])
        
        logger.info(f"Iniciando aplicação no ambiente: {config_class.__name__}")
        logger.info(f"CORS habilitado para: {cors_origins}")

        # Inicialização de extensões
        db.init_app(app)
        jwt = JWTManager(app)
        logger.info("Extensões inicializadas com sucesso")
        
        # Configuração do JWT
        configure_jwt_handlers(jwt, logger)
        
        with app.app_context():
            # Registro de blueprints e banco de dados
            register_blueprints(app, logger)
            initialize_database(app, db, logger)
            
            # Cria diretório para uploads se não existir
            upload_dir = Path(Config.UPLOAD_FOLDER) / 'public'
            upload_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Diretório de uploads configurado em: {upload_dir}")

        # Endpoints utilitários
        register_utility_endpoints(app, db, logger)
        
    except Exception as e:
        logger.critical(f"Falha na inicialização da aplicação: {str(e)}", exc_info=True)
        raise

    return app

def configure_jwt_handlers(jwt, logger):
    """Configura callbacks para tratamento de erros JWT"""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"Token expirado tentou acessar: {jwt_payload.get('sub', 'N/A')}")
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
            "message": "Token inválido ou malformado",
            "code": 401
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.warning("Tentativa de acesso não autorizado")
        return jsonify({
            "status": "error",
            "message": "Token não fornecido",
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

        app.register_blueprint(user_bp, url_prefix='/api/users')
        app.register_blueprint(neural_bp, url_prefix='/api/neural')
        
        logger.info("Blueprints registrados com sucesso")
    except Exception as e:
        logger.error(f"Erro ao registrar blueprints: {str(e)}", exc_info=True)
        raise

def initialize_database(app, db, logger):
    """Inicializa e verifica o banco de dados"""
    try:
        from models.userModel import User
        from models.imageModel import Image
        from models.ObjectRecognitionResultModel import ObjectRecognitionResult

        # Cria tabelas se não existirem
        db.create_all()
        logger.info("Tabelas verificadas/criadas")
        
        # Testa a conexão
        db.session.execute(text("SELECT 1"))
        logger.info("Conexão com o banco de dados OK")
        
    except Exception as e:
        logger.critical(f"Erro na inicialização do banco: {str(e)}", exc_info=True)
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
                "storage": "active" if Path(Config.UPLOAD_FOLDER).exists() else "inactive"
            },
            "environment": app.config.get("ENVIRONMENT", "production"),
            "version": "1.0.0"
        }
        logger.debug("Health check realizado")
        return jsonify(status)

    @app.route('/version')
    def version():
        """Endpoint de versão da API"""
        return jsonify({
            "name": "NeuroVision API",
            "version": "1.0.0",
            "environment": app.config.get("ENVIRONMENT", "production")
        })

    @app.route('/uploads/public/<filename>')
    def serve_uploaded_file(filename):
        """Endpoint para servir arquivos uploadados localmente"""
        try:
            return send_from_directory(
                directory=os.path.join(Config.UPLOAD_FOLDER, 'public'),
                path=filename,
                as_attachment=False
            )
        except FileNotFoundError:
            return jsonify({"error": "Arquivo não encontrado"}), 404

def test_database_connection(db):
    """Testa a conexão com o banco de dados"""
    try:
        db.session.execute(text("SELECT 1"))
        return "connected"
    except Exception as e:
        return f"disconnected: {str(e)}"

# Criação da aplicação
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    debug_mode = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True,
        use_reloader=debug_mode
    )
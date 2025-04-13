import os
from flask import Flask, jsonify, request
from config.config import Config, ProductionConfig
from extensions import db
from flask_jwt_extended import JWTManager
import logging
from datetime import datetime
from flask_cors import CORS
from sqlalchemy import text

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

def create_app(config_class=ProductionConfig):
    """Factory principal da aplicação Flask"""
    app = Flask(__name__)
    
    # Carrega configurações
    app.config.from_object(config_class)
    config_class.init_app(app)  # Inicializa configurações adicionais
    
    # Configura CORS
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": os.environ.get('ALLOWED_ORIGINS', 'http://localhost:4200').split(',')
        }
    })
    
    logger = configure_logging()
    logger.info(f"Iniciando aplicação no ambiente: {config_class.__name__}")
    logger.info(f"Configuração de banco de dados: {app.config['SQLALCHEMY_DATABASE_URI'].split('?')[0]}")
    
    try:
        # Inicializa extensões
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
    register_diagnostic_endpoints(app, logger)  # Novo endpoint de diagnóstico

    @app.before_first_request
    def verify_db_connection():
        try:
            db.session.execute(text("SELECT 1"))
            logger.info("Conexão com o banco de dados estabelecida com sucesso no primeiro request")
        except Exception as e:
            logger.critical(f"Falha na conexão com o banco de dados no primeiro request: {str(e)}")
            # Log da URI sem expor credenciais
            safe_uri = app.config['SQLALCHEMY_DATABASE_URI'].split('@')
            if len(safe_uri) > 1:
                logger.critical(f"URI do banco (parte do host): {safe_uri[1].split('?')[0]}")
            else:
                logger.critical("URI do banco não disponível em formato padrão")

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
        
        app.register_blueprint(user_bp, url_prefix='/api/users')
        app.register_blueprint(neural_bp, url_prefix='/api/neural')
        logger.info("Blueprints registrados com sucesso")
    except ImportError as e:
        logger.error(f"Falha ao importar blueprints: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Falha ao registrar blueprints: {str(e)}", exc_info=True)
        raise

def initialize_database(app, db, logger):
    """Inicializa e verifica o banco de dados"""
    try:
        # Importa modelos para garantir que as tabelas sejam criadas
        from models.userModel import User
        from models.imageModel import Image
        from models.ObjectRecognitionResultModel import ObjectRecognitionResult
        
        # Testa a conexão antes de criar tabelas
        try:
            db.session.execute(text("SELECT 1"))
            logger.info("Conexão com o banco de dados testada com sucesso")
            
            # Só cria tabelas se a conexão estiver OK
            db.create_all()
            logger.info("Tabelas do banco de dados verificadas/criadas")
        except Exception as db_error:
            logger.critical(f"Teste de conexão com o banco de dados falhou: {str(db_error)}", exc_info=True)
            # Verifica configuração do ODBC
            try:
                import subprocess
                odbc_info = subprocess.check_output(['odbcinst', '-j']).decode()
                logger.info(f"Informações do ODBC: {odbc_info}")
                
                drivers = subprocess.check_output(['odbcinst', '-q', '-d']).decode()
                logger.info(f"Drivers ODBC disponíveis: {drivers}")
            except Exception as odbc_error:
                logger.error(f"Não foi possível obter informações do ODBC: {str(odbc_error)}")
            raise db_error
        
    except Exception as e:
        logger.critical(f"Falha na inicialização do banco de dados: {str(e)}", exc_info=True)
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
            },
            "environment": app.config.get("ENV", "production")
        }
        logger.debug("Health check realizado")
        return jsonify(status)

    @app.route('/version')
    def version():
        """Endpoint de versão da aplicação"""
        return jsonify({
            "name": "NeuroVision API",
            "version": "1.0.0",
            "environment": app.config.get("ENV", "production")
        })

def register_diagnostic_endpoints(app, logger):
    """Registra endpoints de diagnóstico"""
    @app.route('/diagnostic')
    def diagnostic():
        """Endpoint para diagnóstico do ambiente e configurações"""
        import os
        import subprocess
        import sys
        
        try:
            # Informações do sistema
            system_info = {
                "python_version": sys.version,
                "platform": sys.platform,
                "cwd": os.getcwd(),
                "env_vars": {
                    "PATH": os.environ.get("PATH", "Não definido"),
                    "LD_LIBRARY_PATH": os.environ.get("LD_LIBRARY_PATH", "Não definido"),
                    "PYTHONPATH": os.environ.get("PYTHONPATH", "Não definido")
                }
            }
            
            # Verificar drivers ODBC instalados
            odbc_info = {}
            try:
                odbc_info["config"] = subprocess.check_output(['odbcinst', '-j']).decode()
            except Exception as e:
                odbc_info["config_error"] = str(e)
                
            try:
                odbc_info["drivers"] = subprocess.check_output(['odbcinst', '-q', '-d']).decode()
            except Exception as e:
                odbc_info["drivers_error"] = str(e)
                
            # Verificar diretórios chave
            dir_check = {}
            paths_to_check = [
                "/usr/lib/x86_64-linux-gnu/odbc",
                "/usr/local/lib/odbc",
                "/opt/microsoft/msodbcsql17"
            ]
            
            for path in paths_to_check:
                try:
                    if os.path.exists(path):
                        dir_check[path] = os.listdir(path)
                    else:
                        dir_check[path] = "Diretório não existe"
                except Exception as e:
                    dir_check[path] = f"Erro ao verificar: {str(e)}"
            
            return jsonify({
                "system": system_info,
                "odbc": odbc_info,
                "directories": dir_check,
                "database_config": {
                    "database_type": "SQL Server",
                    "connection_string_type": "ODBC via pyodbc",
                    "server": os.environ.get("DATABASE_URL", "").split("@")[1].split("/")[0] if "@" in os.environ.get("DATABASE_URL", "") else "Não disponível"
                }
            })
        except Exception as e:
            logger.error(f"Erro no endpoint de diagnóstico: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500

def test_database_connection(db):
    """Testa a conexão com o banco de dados"""
    try:
        db.session.execute(text("SELECT 1"))
        return "connected"
    except Exception as e:
        return f"disconnected: {str(e)}"

# Cria a aplicação usando a configuração apropriada
app = create_app()

if __name__ == "__main__":
    # Configuração para produção no Render
    port = int(os.environ.get("PORT", 10000))  # Render usa porta 10000 por padrão
    app.run(
        host='0.0.0.0',  # Importante para aceitar conexões externas
        port=port,
        debug=os.environ.get('DEBUG_MODE', 'False').lower() == 'true',
        threaded=True
    )
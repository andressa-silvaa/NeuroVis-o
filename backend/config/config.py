
from datetime import timedelta
import os
from pathlib import Path
import logging
from urllib.request import urlretrieve
from sqlalchemy import text

class Config:
    # Configurações de Banco de Dados (SQL Server)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('mysql://', 'mysql+pymysql://')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações JWT (Security)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', "super_secret_key_123!@#")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # Configurações do Servidor
    APP_HOST = os.environ.get('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.environ.get('PORT', 5000))
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

    # Configurações do Imgur
    IMGUR_CLIENT_ID = os.environ.get('IMGUR_CLIENT_ID', 'f74f3693feeb900')
    IMGUR_CLIENT_SECRET = os.environ.get('IMGUR_CLIENT_SECRET', '4f9584bae90e4087a2857da6cb28f0412cc0b403')
    IMGUR_ACCESS_TOKEN = os.environ.get('IMGUR_ACCESS_TOKEN', 'seu_access_token')

    # Configurações do YOLO (com fallback para download)
    YOLO_WEIGHTS_DIR = Path(__file__).resolve().parent.parent / 'model_weights'
    YOLO_WEIGHTS_PATH = YOLO_WEIGHTS_DIR / 'best.pt'
    YOLO_WEIGHTS_URL = os.environ.get('YOLO_WEIGHTS_URL', '')  # Opcional: URL para download
    
    # Configurações de Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads/images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    @classmethod
    def init_app(cls, app):
        """Inicialização adicional da aplicação"""
        # Configuração de pastas
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
        cls.YOLO_WEIGHTS_DIR.mkdir(exist_ok=True)
        
        # Verificação/Download dos pesos YOLO
        cls._ensure_yolo_weights()

    @classmethod
    def _ensure_yolo_weights(cls):
        """Garante que os pesos YOLO estão disponíveis"""
        if cls.YOLO_WEIGHTS_PATH.exists():
            logging.info(f"Pesos YOLO encontrados em: {cls.YOLO_WEIGHTS_PATH}")
            return
            
        if cls.YOLO_WEIGHTS_URL:
            try:
                logging.info(f"Baixando pesos YOLO de {cls.YOLO_WEIGHTS_URL}")
                urlretrieve(cls.YOLO_WEIGHTS_URL, cls.YOLO_WEIGHTS_PATH)
                logging.info("Download dos pesos YOLO concluído")
                return
            except Exception as e:
                logging.error(f"Falha no download dos pesos: {str(e)}")
        
        # Mensagem de erro detalhada
        current_dir = Path.cwd()
        dir_contents = "\n".join([str(p) for p in cls.YOLO_WEIGHTS_DIR.glob('*')])
        error_msg = (
            f"Arquivo de pesos YOLO não encontrado em: {cls.YOLO_WEIGHTS_PATH}\n"
            f"Diretório atual: {current_dir}\n"
            f"Conteúdo do diretório de pesos:\n{dir_contents}\n"
            f"Execute o script a partir de: {Path(__file__).parent}"
        )
        logging.critical(error_msg)
        raise FileNotFoundError(error_msg)

class ProductionConfig(Config):
    DEBUG_MODE = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30
    }

class DevelopmentConfig(Config):
    DEBUG_MODE = True
    SQLALCHEMY_ECHO = True
    ENVIRONMENT = 'development'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    ENVIRONMENT = 'testing'

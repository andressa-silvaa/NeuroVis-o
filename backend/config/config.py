from datetime import timedelta
import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://andressa_sql_user:%40AndressaSilva123@DESKTOP-PRCKVPI/neurovision_db?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "super_secret_key_123!@#"  
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)  
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7) 
    APP_HOST = '0.0.0.0'  # ou 'localhost' ou o IP desejado
    APP_PORT = 5000
    DEBUG_MODE = True   
    # Adicione ao config.py
    IMGUR_CLIENT_ID = 'f74f3693feeb900'  
    IMGUR_CLIENT_SECRET = '4f9584bae90e4087a2857da6cb28f0412cc0b403'  
    IMGUR_ACCESS_TOKEN = 'seu_access_token'
    # Configurações para processamento de imagens
    YOLO_WEIGHTS_PATH = 'C:/repo/NeuroVis-o/treino-rede-neural-yolov8/train34/weights/best.pt'
    UPLOAD_FOLDER = 'uploads/images'  # Aqui você define o caminho para a pasta de uploads

    # Criar o diretório caso não exista
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://USUÁRIO:SENHA@SERVIDOR/NOME_BANCO?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'CHAVE-SECRETA-FORTE-AQUI'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)  
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)    
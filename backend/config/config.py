from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://andressa_sql_user:%40AndressaSilva123@DESKTOP-PRCKVPI/neurovision_db?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "super_secret_key_123!@#"  
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)  
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)    

from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'Users'
    __table_args__ = {'schema': 'dbo'}
    
    UserID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(255), nullable=False, unique=True)
    PasswordHash = db.Column(db.String(255), nullable=False)
    FullName = db.Column(db.String(255), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Cria um hash da senha e armazena"""
        self.PasswordHash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.PasswordHash, password)

    def __repr__(self):
        return f'<User {self.Email}>'
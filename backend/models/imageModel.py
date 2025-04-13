from extensions import db
from datetime import datetime

class Image(db.Model):
    __tablename__ = 'Images'
    # Remover o uso de 'schema' no MySQL
    __table_args__ = {}  # Não é necessário usar schema no MySQL
    
    ImageID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)  # Remover 'dbo.' se não for usado
    ImagePath = db.Column(db.String(500), nullable=False)
    UploadedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com 'ObjectRecognitionResult'
    recognition_results = db.relationship(
        'ObjectRecognitionResult', 
        back_populates='image',
        cascade='all, delete-orphan',
        lazy=True
    )

    def __repr__(self):
        return f'<Image {self.ImageID}>'

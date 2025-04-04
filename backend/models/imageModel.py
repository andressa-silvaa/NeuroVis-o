from extensions import db
from datetime import datetime

class Image(db.Model):
    __tablename__ = 'Images'
    __table_args__ = {'schema': 'dbo'} 
    ImageID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('dbo.Users.UserID'), nullable=False) 
    ImagePath = db.Column(db.String(500), nullable=False)
    UploadedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    recognition_results = db.relationship(
        'ObjectRecognitionResult', 
        back_populates='image',
        cascade='all, delete-orphan',
        lazy=True
    )

    def __repr__(self):
        return f'<Image {self.ImageID}>'

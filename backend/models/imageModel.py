from extensions import db
from datetime import datetime

class Image(db.Model):
    __tablename__ = 'Images'
    
    ImageID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'), nullable=False)
    ImagePath = db.Column(db.String(500), nullable=False)
    UploadedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    recognition_results = db.relationship('ObjectRecognitionResult', backref='image', lazy=True)

class ObjectRecognitionResult(db.Model):
    __tablename__ = 'ObjectRecognitionResults'
    
    ResultID = db.Column(db.Integer, primary_key=True)
    ImageID = db.Column(db.Integer, db.ForeignKey('Images.ImageID'), nullable=False)
    RecognizedObjects = db.Column(db.Text, nullable=False)
    ProcessedImagePath = db.Column(db.String(500), nullable=False)
    AnalyzedAt = db.Column(db.DateTime, default=datetime.utcnow)
    Accuracy = db.Column(db.Float, nullable=False)
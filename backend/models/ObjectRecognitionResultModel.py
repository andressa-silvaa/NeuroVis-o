from extensions import db
from datetime import datetime

class ObjectRecognitionResult(db.Model):
    __tablename__ = 'ObjectRecognitionResults'
    
    ResultID = db.Column(db.Integer, primary_key=True)
    ImageID = db.Column(db.Integer, db.ForeignKey('Images.ImageID'), nullable=False)
    RecognizedObjects = db.Column(db.Text, nullable=False)
    ProcessedImagePath = db.Column(db.String(500), nullable=False)
    AnalyzedAt = db.Column(db.DateTime, default=datetime.utcnow)
    Accuracy = db.Column(db.Float, nullable=False)
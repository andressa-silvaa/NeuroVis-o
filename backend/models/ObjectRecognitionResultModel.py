from extensions import db
from sqlalchemy.dialects.mssql import TEXT
from datetime import datetime

class ObjectRecognitionResult(db.Model):
    __tablename__ = 'ObjectRecognitionResults'
    __table_args__ = {'schema': 'dbo', 'extend_existing': True}
    
    ResultID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ImageID = db.Column(
        db.Integer, 
        db.ForeignKey('dbo.Images.ImageID', ondelete='CASCADE'), 
        nullable=False
    )
    RecognizedObjects = db.Column(TEXT, nullable=False)
    ProcessedImagePath = db.Column(db.String(255), nullable=False)
    AnalyzedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    Accuracy = db.Column(db.Float, nullable=True)
    InferenceTimeMs = db.Column(db.Integer, nullable=True)
    TotalTimeMs = db.Column(db.Integer, nullable=True)  
    ConfidenceAvg = db.Column(db.Float, nullable=True)
    ObjectsCount = db.Column(db.Integer, nullable=True)
    DetectionDetails = db.Column(TEXT, nullable=True)
    
    image = db.relationship('Image', back_populates='recognition_results')

    def __repr__(self):
        return f'<ObjectRecognitionResult {self.ResultID} - Image {self.ImageID}>'

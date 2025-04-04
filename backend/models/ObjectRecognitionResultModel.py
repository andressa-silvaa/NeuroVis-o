from extensions import db
from datetime import datetime
from sqlalchemy.dialects.mssql import TEXT, NVARCHAR
from typing import Dict, List
import json

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
    Precision = db.Column(db.Float, nullable=True)
    Recall = db.Column(db.Float, nullable=True)
    InferenceTimeMs = db.Column(db.Integer, nullable=True)
    PreprocessTimeMs = db.Column(db.Integer, nullable=True)
    PostprocessTimeMs = db.Column(db.Integer, nullable=True)
    ConfidenceAvg = db.Column(db.Float, nullable=True)
    ObjectsCount = db.Column(db.Integer, nullable=True)
    DetectionDetails = db.Column(NVARCHAR(length=2**31-1), nullable=True)
    
    image = db.relationship('Image', back_populates='recognition_results')
    
    def set_detection_details(self, results: List[Dict]):
        """Helper para serializar os detalhes da detecção"""
        self.DetectionDetails = json.dumps({
            'objects': results,
            'metadata': {
                'processed_at': datetime.utcnow().isoformat(),
                'model_version': 'yolov8'
            }
        })
    
    def get_detection_details(self) -> Dict:
        """Helper para desserializar os detalhes"""
        return json.loads(self.DetectionDetails) if self.DetectionDetails else None

    def __repr__(self):
        return f'<ObjectRecognitionResult {self.ResultID} - Image {self.ImageID}>'
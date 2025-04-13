from extensions import db
from datetime import datetime

class ObjectRecognitionResult(db.Model):
    __tablename__ = 'ObjectRecognitionResults'
    # Remova o esquema, pois no MySQL isso não é utilizado da mesma forma
    __table_args__ = {'extend_existing': True}
    
    ResultID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ImageID = db.Column(
        db.Integer, 
        db.ForeignKey('Images.ImageID', ondelete='CASCADE'),  # Remova 'dbo.' se não usar esquema
        nullable=False
    )
    RecognizedObjects = db.Column(db.String(255), nullable=False)  # Usando String no lugar de TEXT
    ProcessedImagePath = db.Column(db.String(255), nullable=False)
    AnalyzedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    Accuracy = db.Column(db.Float, nullable=True)
    InferenceTimeMs = db.Column(db.Integer, nullable=True)
    TotalTimeMs = db.Column(db.Integer, nullable=True)  
    ConfidenceAvg = db.Column(db.Float, nullable=True)
    ObjectsCount = db.Column(db.Integer, nullable=True)
    DetectionDetails = db.Column(db.String(255), nullable=True)  # Usando String no lugar de TEXT
    
    image = db.relationship('Image', back_populates='recognition_results')

    def __repr__(self):
        return f'<ObjectRecognitionResult {self.ResultID} - Image {self.ImageID}>'

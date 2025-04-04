from extensions import db
from models.imageModel import Image
from models.ObjectRecognitionResultModel import ObjectRecognitionResult
from datetime import datetime
import json

def save_image(user_id: int, image_path: str) -> int:
    """
    Salva a imagem no banco de dados e retorna o ID
    """
    try:
        new_image = Image(
            UserID=user_id,
            ImagePath=image_path,
            UploadedAt=datetime.utcnow()
        )
        db.session.add(new_image)
        db.session.commit()
        return new_image.ImageID
    except Exception as e:
        db.session.rollback()
        raise e

def save_recognition_result(
    image_id: int,
    recognized_objects: list,
    processed_image_path: str,
    accuracy: float,
    precision: float,
    recall: float, 
    inference_time: float
) -> int:
    """
    Salva os resultados da análise com todas as novas métricas
    """
    try:
        new_result = ObjectRecognitionResult(
            ImageID=image_id,
            RecognizedObjects=json.dumps(recognized_objects), 
            ProcessedImagePath=processed_image_path,
            Accuracy=accuracy,
            Precision=precision,
            Recall=recall, 
            InferenceTimeMs=inference_time,
            AnalyzedAt=datetime.utcnow()
        )
        db.session.add(new_result)
        db.session.commit()
        return new_result.ResultID
    except Exception as e:
        db.session.rollback()
        raise e

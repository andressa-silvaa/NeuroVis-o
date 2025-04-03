from extensions import db
from models.imageModel import Image, ObjectRecognitionResult
from datetime import datetime

def save_image(user_id, image_path):
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

def save_recognition_result(image_id, recognized_objects, processed_image_path, accuracy):
    try:
        new_result = ObjectRecognitionResult(
            ImageID=image_id,
            RecognizedObjects=str(recognized_objects),  # Serializa como string
            ProcessedImagePath=processed_image_path,
            Accuracy=accuracy,
            AnalyzedAt=datetime.utcnow()
        )
        db.session.add(new_result)
        db.session.commit()
        return new_result.ResultID
    except Exception as e:
        db.session.rollback()
        raise e
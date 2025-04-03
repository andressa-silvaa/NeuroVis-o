from repositories.neuralNetworkRepository import save_image, save_recognition_result
from ultralytics import YOLO
import os
import uuid
from datetime import datetime
from config.config import Config
import shutil

class NeuralNetworkService:
    def __init__(self):
        self.model = YOLO(Config.YOLO_WEIGHTS_PATH)
        self.processed_images_dir = Config.PROCESSED_IMAGES_DIR
        os.makedirs(self.processed_images_dir, exist_ok=True)

    def analyze_image(self, image_path, user_id):
        # Executa a detecção
        results = self.model(image_path)
        
        # Processa os resultados
        detection_img = results[0].plot()
        recognized_objects = []
        
        for box in results[0].boxes:
            recognized_objects.append({
                'class_name': results[0].names[int(box.cls)],
                'confidence': float(box.conf),
                'bbox': box.xyxy[0].tolist()
            })

        # Calcula acurácia média (simplificado)
        accuracy = sum([obj['confidence'] for obj in recognized_objects]) / max(1, len(recognized_objects))

        # Salva a imagem processada
        processed_filename = f"processed_{uuid.uuid4()}.jpg"
        processed_path = os.path.join(self.processed_images_dir, processed_filename)
        detection_img.save(processed_path)

        # Salva no banco de dados
        image_url = f"{Config.IMAGES_BASE_URL}/{processed_filename}"
        image_id = save_image(user_id, image_url)
        
        save_recognition_result(
            image_id=image_id,
            recognized_objects=recognized_objects,
            processed_image_path=image_url,
            accuracy=accuracy
        )

        return {
            'processed_image_url': image_url,
            'recognized_objects': [obj['class_name'] for obj in recognized_objects],
            'accuracy': accuracy,
            'image_id': image_id
        }

# Instância singleton do serviço
neural_service = NeuralNetworkService()

def analyze_image(image_path, user_id):
    return neural_service.analyze_image(image_path, user_id)
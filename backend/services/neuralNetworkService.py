import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import cv2
from config.config import Config
from repositories.neuralNetworkRepository import save_image, save_recognition_result
from services.detectObjectService import get_detection_results

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NeuralNetworkService:
    def __init__(self):
        """Inicializa o serviço com cliente Imgur"""
        try:
            self.imgur_client = ImgurClient(
                Config.IMGUR_CLIENT_ID, 
                Config.IMGUR_CLIENT_SECRET
            )
            logger.info("Serviço neural configurado")
        except Exception as e:
            logger.error(f"Falha ao configurar Imgur: {str(e)}")
            raise

    def _upload_to_imgur(self, image_path: str) -> str:
        """Faz upload de uma imagem para o Imgur"""
        try:
            response = self.imgur_client.upload_from_path(image_path, anon=True)
            return response['link']
        except ImgurClientError as e:
            error_msg = "Limite do Imgur atingido" if 'rate limit' in str(e) else f"Erro no Imgur: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def analyze_image(self, image_path: str, user_id: int) -> Dict:
        """
        Processa imagem completa: detecção, upload e salvamento.
        """
        try:
            detection_img, detected_objects, metrics = get_detection_results(image_path)
            
            accuracy = sum(obj['confidence'] for obj in detected_objects) / max(1, len(detected_objects))
            recall = metrics.get('recall', 0) 
            
            filename = f"processed_{uuid.uuid4()}.jpg"
            temp_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            
            cv2.imwrite(temp_path, detection_img)  
            
            try:
                image_url = self._upload_to_imgur(temp_path)
                logger.info(f"Imagem enviada: {image_url}")
                
                image_id = save_image(user_id, image_url)
                save_recognition_result(
                    image_id=image_id,
                    recognized_objects=detected_objects,
                    processed_image_path=image_url,
                    accuracy=accuracy,
                    precision=metrics['precision'],
                    recall=recall,  
                    inference_time=metrics['inference_time']
                )
                
                return {
                    'image_id': image_id,
                    'image_url': image_url,
                    'objects': [obj['class_name'] for obj in detected_objects],
                    'accuracy': round(accuracy, 4),
                    'metrics': metrics
                }
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"Falha na análise: {str(e)}")
            raise


neural_service = NeuralNetworkService()

def analyze_image(image_path: str, user_id: int) -> Dict:
    """Interface pública para análise de imagens"""
    return neural_service.analyze_image(image_path, user_id)

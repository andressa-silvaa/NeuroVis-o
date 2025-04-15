import os
import uuid
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import cv2
import json
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
            logger.info("Serviço neural configurado com Imgur")
        except Exception as e:
            logger.error(f"Falha ao configurar Imgur: {str(e)}")
            self.imgur_client = None  # Permite o funcionamento sem Imgur

    def _upload_to_imgur(self, image_path: str, image_uuid: str, max_retries: int = 3) -> Optional[str]:
        """
        Faz upload de uma imagem para o Imgur com retentativas e tratamento robusto de erros
        Retorna None se o upload falhar após todas as tentativas
        """
        if not self.imgur_client:
            logger.warning("Upload ao Imgur desabilitado - cliente não configurado")
            return None

        for attempt in range(max_retries):
            try:
                logger.info(f"Tentando upload para Imgur (tentativa {attempt + 1}/{max_retries})")
                response = self.imgur_client.upload_from_path(image_path, anon=True)
                
                # Log detalhado da resposta (sem dados sensíveis)
                logger.debug(f"Resposta do Imgur: { {k: v for k, v in response.items() if k not in ['deletehash', 'account_url']} }")
                
                image_url = f"{response['link']}?uuid={image_uuid}"
                logger.info(f"Upload para Imgur bem-sucedido: {image_url}")
                return image_url
                
            except ImgurClientError as e:
                if 'rate limit' in str(e).lower():
                    wait_time = (attempt + 1) * 5  # Backoff exponencial
                    logger.warning(f"Limite de taxa do Imgur atingido. Tentando novamente em {wait_time} segundos...")
                    time.sleep(wait_time)
                    continue
                
                logger.error(f"Erro do cliente Imgur: {str(e)}")
                return None
                
            except Exception as e:
                logger.error(f"Erro inesperado ao enviar para Imgur: {str(e)}")
                if attempt == max_retries - 1:
                    return None
                time.sleep(2)  # Pequena pausa antes de tentar novamente

        return None

    def _save_image_locally(self, image: bytes, filename: str) -> str:
        """Salva a imagem localmente e retorna a URL relativa"""
        try:
            public_dir = os.path.join(Config.UPLOAD_FOLDER, "public")
            os.makedirs(public_dir, exist_ok=True)
            local_path = os.path.join(public_dir, filename)
            
            cv2.imwrite(local_path, image)
            return f"/uploads/public/{filename}"
        except Exception as e:
            logger.error(f"Falha ao salvar imagem localmente: {str(e)}")
            raise Exception("Falha ao armazenar imagem localmente")

    def analyze_image(self, image_path: str, user_id: int, image_uuid: str = None) -> Dict:
        """
        Processa imagem completa: detecção, upload (Imgur ou local) e salvamento.
        """
        try:
            image_uuid = image_uuid or str(uuid.uuid4())
            logger.info(f"Iniciando análise da imagem {image_uuid}")

            # Processa a imagem com YOLO
            detection_img, detected_objects, raw_metrics = get_detection_results(image_path)
            accuracy = sum(obj['confidence'] for obj in detected_objects) / max(1, len(detected_objects))
            filename = f"processed_{image_uuid}.jpg"
            temp_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            
            try:
                # Salva a imagem processada temporariamente
                cv2.imwrite(temp_path, detection_img)
                
                # Tenta upload no Imgur primeiro
                image_url = self._upload_to_imgur(temp_path, image_uuid)
                
                # Fallback para armazenamento local se Imgur falhar
                if not image_url:
                    logger.warning("Usando fallback para armazenamento local")
                    image_url = self._save_image_locally(detection_img, filename)
                
                # Salva no banco de dados
                image_id = save_image(user_id, image_url)
                detected_objects_json = json.dumps(detected_objects)
                
                save_recognition_result(
                    image_id=image_id,
                    recognized_objects=detected_objects_json,
                    processed_image_path=image_url,
                    accuracy=accuracy,
                    inference_time=raw_metrics.get('inference_time'),
                    total_time=raw_metrics.get('total_time'),  
                    confidence_avg=accuracy,
                    objects_count=len(detected_objects),
                    detection_details=detected_objects_json
                )

                metrics = {
                    'accuracy': round(accuracy, 4),
                    'inference_time': raw_metrics.get('inference_time'),
                    'total_time': raw_metrics.get('total_time') 
                }

                return {
                    'image_id': image_id,
                    'image_url': image_url,
                    'objects': [obj['class_name'] for obj in detected_objects],
                    'accuracy': round(accuracy, 4),
                    'metrics': metrics,
                    'objects_count': len(detected_objects) 
                }
                
            finally:
                # Limpeza do arquivo temporário
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"Falha na análise da imagem {image_uuid}: {str(e)}", exc_info=True)
            raise Exception(f"Erro ao processar imagem: {str(e)}")

# Instância global
neural_service = NeuralNetworkService()

def analyze_image(image_path: str, user_id: int, image_uuid: str = None) -> Dict:
    """Interface pública para análise de imagens"""
    return neural_service.analyze_image(image_path, user_id, image_uuid)
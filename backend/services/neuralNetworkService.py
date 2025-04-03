import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
from ultralytics import YOLO
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError

from config.config import Config
from repositories.neuralNetworkRepository import save_image, save_recognition_result

logger = logging.getLogger(__name__)

class NeuralNetworkService:
    def __init__(self):
        """Inicializa o serviço carregando o modelo YOLO e configurando o cliente Imgur"""
        try:
            # Carrega o modelo YOLO
            self.model = YOLO(Config.YOLO_WEIGHTS_PATH)
            logger.info("Modelo YOLO carregado com sucesso")
            
            # Configura o cliente Imgur
            self.imgur_client = ImgurClient(
                Config.IMGUR_CLIENT_ID, 
                Config.IMGUR_CLIENT_SECRET
            )
            logger.info("Cliente Imgur configurado")
            
        except Exception as e:
            logger.error(f"Falha ao inicializar serviço: {str(e)}")
            raise

    def _upload_to_imgur(self, image_path: str) -> str:
        """Faz upload de uma imagem para o Imgur e retorna a URL"""
        try:
            response = self.imgur_client.upload_from_path(
                image_path,
                config=None,
                anon=True
            )
            return response['link']
        except ImgurClientError as e:
            if 'rate limit' in str(e).lower():
                logger.error("Limite de uploads diário atingido no Imgur")
                raise Exception("Limite de uploads excedido. Tente novamente mais tarde.")
            else:
                logger.error(f"Erro no upload para Imgur: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Erro inesperado ao fazer upload: {str(e)}")
            raise

    def _process_detection_results(self, results) -> Tuple[List[Dict], float]:
        """Processa os resultados da detecção e retorna objetos encontrados e acurácia"""
        recognized_objects = []
        total_confidence = 0.0
        
        for box in results[0].boxes:
            obj_info = {
                'class_id': int(box.cls),
                'class_name': results[0].names[int(box.cls)],
                'confidence': float(box.conf),
                'bbox': box.xyxy[0].tolist()
            }
            recognized_objects.append(obj_info)
            total_confidence += float(box.conf)
        
        accuracy = total_confidence / max(1, len(recognized_objects))
        return recognized_objects, accuracy

    def analyze_image(self, image_path: str, user_id: int) -> Dict:
        """
        Analisa uma imagem e retorna os resultados processados
        
        Args:
            image_path: Caminho local para a imagem
            user_id: ID do usuário que solicitou a análise
            
        Returns:
            Dicionário com:
            - processed_image_url: URL da imagem processada no Imgur
            - recognized_objects: Lista de objetos detectados
            - accuracy: Acurácia média das detecções
            - image_id: ID da imagem no banco de dados
        """
        try:
            # Validação inicial
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Arquivo de imagem não encontrado: {image_path}")

            logger.info(f"Iniciando análise da imagem: {image_path}")
            
            # Executa a detecção
            results = self.model(image_path)
            detection_img = results[0].plot()
            
            # Processa os resultados
            recognized_objects, accuracy = self._process_detection_results(results)
            
            # Salva temporariamente a imagem processada
            temp_filename = f"processed_{uuid.uuid4()}.jpg"
            temp_path = os.path.join('/tmp', temp_filename)
            detection_img.save(temp_path)
            
            try:
                # Faz upload para o Imgur
                image_url = self._upload_to_imgur(temp_path)
                logger.info(f"Imagem enviada para Imgur: {image_url}")
                
                # Salva no banco de dados
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
                
            finally:
                # Limpeza do arquivo temporário
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"Erro durante análise da imagem: {str(e)}")
            raise

# Instância singleton do serviço
neural_service = NeuralNetworkService()

def analyze_image(image_path: str, user_id: int) -> Dict:
    """Função pública para análise de imagens"""
    return neural_service.analyze_image(image_path, user_id)
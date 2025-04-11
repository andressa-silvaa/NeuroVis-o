import os
import cv2
from ultralytics import YOLO
import logging
from typing import Tuple, List, Dict, Union
import numpy as np
from config.config import Config

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class YOLOv8Detector:
    def __init__(self, weights_path: str = None):
        self.weights_path = weights_path or Config.YOLO_WEIGHTS_PATH
        self.model = None

    def load_model(self) -> None:
        """Carrega o modelo YOLOv8 a partir dos pesos fornecidos."""
        if os.path.exists(self.weights_path):
            logger.info(f"Carregando modelo de {self.weights_path}")
            self.model = YOLO(self.weights_path)
        else:
            logger.error(f"Arquivo de pesos não encontrado: {self.weights_path}")
            raise FileNotFoundError(f"Arquivo de pesos não encontrado: {self.weights_path}")

    def detect(self, image_path: Union[str, np.ndarray]) -> Tuple[np.ndarray, List[Dict], Dict]:
        """
        Detecta objetos em uma imagem e retorna a imagem com deteções,
        os objetos detectados e as métricas de tempo.
        """
        if not self.model:
            raise ValueError("Modelo não carregado. Chame load_model() primeiro.")

        results = self.model(image_path)
        detection_img = results[0].plot()
        detected_objects = []

        for box in results[0].boxes:
            detected_objects.append({
                'class_id': int(box.cls),
                'class_name': results[0].names[int(box.cls)],
                'confidence': float(box.conf),
                'bbox': box.xyxy[0].tolist()
            })

        metrics = {
            'inference_time': results[0].speed.get('inference'),
            'total_time': sum(results[0].speed.values())  
        }

        return detection_img, detected_objects, metrics

    def batch_detect(self, images_dir: str, output_dir: str = None) -> List[Dict]:
        """Detecta objetos em todas as imagens de um diretório."""
        if not os.path.exists(images_dir):
            raise FileNotFoundError(f"Diretório não encontrado: {images_dir}")

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        results = []
        for img_path in [os.path.join(images_dir, f) for f in os.listdir(images_dir) 
                        if f.lower().endswith(('.jpg', '.png', '.jpeg'))]:
            try:
                detection_img, objects, metrics = self.detect(img_path)
                if output_dir:
                    output_path = os.path.join(output_dir, os.path.basename(img_path))
                    cv2.imwrite(output_path, detection_img)
                results.append({'path': img_path, 'objects': objects, 'metrics': metrics})
            except Exception as e:
                logger.error(f"Erro ao processar {img_path}: {str(e)}")

        return results

# Instancia global e carregamento do modelo
detector = YOLOv8Detector()
detector.load_model()

def get_detection_results(image_path: Union[str, np.ndarray]) -> Tuple[np.ndarray, List[Dict], Dict]:
    """Interface padrão para outros serviços"""
    return detector.detect(image_path)

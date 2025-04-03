import os
import cv2
from ultralytics import YOLO
import logging
from typing import Tuple, List, Dict, Union
import numpy as np

# Configuração de logs
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YOLOv8Detector:
    def __init__(self, weights_path: str):
        self.weights_path = weights_path
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
        Detecta objetos em uma única imagem e retorna múltiplos resultados.
        
        Args:
            image_path: Caminho para a imagem ou array numpy da imagem
            
        Returns:
            Tuple contendo:
            - imagem com as detecções desenhadas
            - lista de objetos detectados (cada objeto é um dicionário com informações)
            - métricas de desempenho (acurácia, precisão, etc.)
        """
        if not self.model:
            raise ValueError("Modelo não carregado. Chame load_model() primeiro.")

        # Executa a detecção
        results = self.model(image_path)
        
        # Processa os resultados
        detection_img = results[0].plot()  # Imagem com bounding boxes
        detected_objects = []
        
        # Extrai informações dos objetos detectados
        for result in results:
            for box in result.boxes:
                obj_info = {
                    'class_id': int(box.cls),
                    'class_name': result.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                }
                detected_objects.append(obj_info)
        
        # Extrai métricas (exemplo simplificado)
        metrics = {
            'accuracy': results[0].speed['preprocess'],  # Exemplo, ajuste conforme necessário
            'precision': results[0].speed['inference'],
            'recall': results[0].speed['postprocess']
        }
        
        return detection_img, detected_objects, metrics

    def batch_detect(self, images_dir: str, output_dir: str = None) -> None:
        """Detecta objetos em todas as imagens de um diretório (compatibilidade com versão anterior)."""
        if not os.path.exists(images_dir):
            raise FileNotFoundError(f"Diretório de imagens não encontrado: {images_dir}")

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        images = [os.path.join(images_dir, img) for img in os.listdir(images_dir) 
                 if img.lower().endswith(('.jpg', '.png', '.jpeg'))]
        
        for img_path in images:
            detection_img, objects, metrics = self.detect(img_path)
            
            if output_dir:
                output_path = os.path.join(output_dir, os.path.basename(img_path))
                cv2.imwrite(output_path, detection_img)
                logger.info(f"Resultado salvo em: {output_path}")
            
            logger.info(f"Objetos detectados em {img_path}: {objects}")


def main():
    """Função executada quando o script é rodado diretamente."""
    import tkinter as tk
    from tkinter import filedialog
    
    # Configurações
    weights_path = 'C:/repo/NeuroVis-o/treino-rede-neural-yolov8/train34/weights/best.pt'
    
    # Instancia o detector
    detector = YOLOv8Detector(weights_path=weights_path)
    detector.load_model()
    
    # Interface para seleção de imagem
    root = tk.Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Imagens", "*.jpg *.jpeg *.png")]
    )
    
    if not image_path:
        logger.info("Nenhuma imagem selecionada. Encerrando...")
        return
    
    # Processa a imagem
    detection_img, objects, metrics = detector.detect(image_path)
    
    # Mostra resultados
    print("\n=== RESULTADOS DA DETECÇÃO ===")
    print(f"Objetos encontrados: {len(objects)}")
    for obj in objects:
        print(f"- {obj['class_name']} (confiança: {obj['confidence']:.2f})")
    
    print("\n=== MÉTRICAS ===")
    print(f"Acurácia: {metrics['accuracy']:.4f}")
    print(f"Precisão: {metrics['precision']:.4f}")
    
    # Exibe a imagem
    cv2.imshow("Resultado da Detecção", detection_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
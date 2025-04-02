import os
from ultralytics import YOLO
import logging

# Configuração de logs
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YOLOv8Detector:
    def __init__(self, weights_path, images_dir):
        self.weights_path = weights_path
        self.images_dir = images_dir
        self.model = None

    def load_model(self):
        """Carrega o modelo a partir do melhor checkpoint"""
        if os.path.exists(self.weights_path):
            logger.info(f"Carregando modelo de {self.weights_path}")
            self.model = YOLO(self.weights_path)
        else:
            logger.error(
                f"Arquivo de pesos não encontrado: {self.weights_path}")
            raise FileNotFoundError(
                f"Arquivo de pesos não encontrado: {self.weights_path}")

    def detect_images(self, output_dir=None):
        """Detecta objetos em todas as imagens da pasta especificada e salva os resultados."""
        if not self.model:
            logger.error(
                "Modelo não carregado. Por favor, carregue o modelo primeiro.")
            raise ValueError(
                "Modelo não carregado. Por favor, carregue o modelo primeiro.")

        if not os.path.exists(self.images_dir):
            logger.error(
                f"Diretório de imagens não encontrado: {self.images_dir}")
            raise FileNotFoundError(
                f"Diretório de imagens não encontrado: {self.images_dir}")

        # Cria o diretório de saída, se não existir
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Diretório de saída criado: {output_dir}")

        images = [os.path.join(self.images_dir, img) for img in os.listdir(
            self.images_dir) if img.endswith(('.jpg', '.png', '.jpeg'))]
        if not images:
            logger.warning(
                f"Nenhuma imagem encontrada no diretório: {self.images_dir}")
            return

        logger.info(f"Iniciando detecção em {len(images)} imagens...")
        for img_path in images:
            logger.info(f"Detectando objetos em: {img_path}")
            results = self.model(img_path)

            # Salva as imagens com as bounding boxes
            if output_dir:
                for i, result in enumerate(results):
                    output_path = os.path.join(
                        output_dir, os.path.basename(img_path))
                    result.save(output_path)
                    logger.info(f"Resultado salvo em: {output_path}")

        logger.info("Detecção concluída.")


if __name__ == "__main__":
    # Caminho para o melhor peso detectado no treinamento
    best_weights_path = 'E:/APS6/NeuroVis-o/runs/detect/train34/weights/best.pt'

    # Caminho para a pasta de imagens de teste
    test_images_dir = 'E:/APS6/NeuroVis-o/backend/dataset/images/test'

    # Diretório de saída para salvar as detecções
    output_dir = 'E:/APS6/NeuroVis-o/runs/detect/detections'

    # Instanciando o detector
    detector = YOLOv8Detector(
        weights_path=best_weights_path, images_dir=test_images_dir)

    # Carregando o modelo
    detector.load_model()

    # Realizando a detecção nas imagens e salvando os resultados
    detector.detect_images(output_dir=output_dir)

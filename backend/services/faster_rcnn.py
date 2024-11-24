import torch
import pandas as pd
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader, random_split
import torchvision.transforms as T
import logging
from pathlib import Path

# Configuração dos logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verificar a disponibilidade de GPU
logger.info(torch.version.cuda)
logger.info("CUDA disponível: %s", torch.cuda.is_available())
logger.info("Número de GPUs disponíveis: %d", torch.cuda.device_count())
if torch.cuda.is_available():
    logger.info("Nome da GPU: %s", torch.cuda.get_device_name(0))
else:
    logger.info("Nenhuma GPU detectada")

# Definição do mapeamento de classes global
class_mapping = {
    'furadeira': 0, 'Guindaste': 1, 'Lixadeira': 2, 'Madeira': 3,
    'Marreta': 4, 'Capacete': 5, 'Pessoa': 6, 'Máscara': 7, 'Colete de Segurança': 8,
    'Máquinas': 9, 'Cone de Segurança': 10, 'Veículo': 11, 'Pá': 12, 'Parafusadeira': 13,
    'Armário': 14, 'Recipiente de resíduos': 15, 'Ferramenta': 16, 'Porta': 17, 'Castelo': 18,
    'Cadeira': 19, 'Faca': 20, 'Saco plástico': 21, 'Casa': 22, 'Luva': 23, 'Janela': 24,
    'Pia': 25, 'Lâmpada': 26, 'Arranha-céu': 27, 'Chave de fenda': 28, 'Edifício de escritório': 29,
    'Caneta': 30, 'Ventilador mecânico': 31, 'Maçaneta': 32, 'Caminhão': 33, 'Tesoura': 34,
    'Ventilador de teto': 35, 'Bota': 36, 'Prego': 37, 'Edifício': 38, 'Martelo': 39,
    'Calculadora': 40, 'Serra elétrica': 41, 'Telha': 42, 'Tinta': 43
}


class CustomDataset(Dataset):
    def __init__(self, annotations_file, img_dir, transform=None):
        logger.info("[INFO] Carregando anotações e preparando dataset...")
        self.annotations = pd.read_csv(
            annotations_file, encoding='ISO-8859-1', dtype=str)
        self.img_dir = img_dir
        self.transform = transform
        logger.info(
            f"[INFO] Dataset carregado com {len(self.annotations)} exemplos.")

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        img_name = os.path.join(self.img_dir, self.annotations.iloc[idx, 0])
        image = cv2.imread(img_name)
        if image is None:
            raise ValueError(f"Não foi possível carregar a imagem: {img_name}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = self.annotations.iloc[idx, 1:5].values.astype(
            np.float32).reshape(-1, 4)

        label = self.annotations.iloc[idx, 5]
        label_num = class_mapping.get(label, -1)

        if label_num == -1:
            logger.warning(
                f"AVISO: Classe '{label}' não encontrada no mapeamento")

        target = {
            "boxes": torch.tensor(boxes, dtype=torch.float32),
            "labels": torch.tensor([label_num], dtype=torch.int64)
        }

        if self.transform:
            image = self.transform(image)

        return image, target


class YOLOModel:
    def __init__(self, weights='yolov5s', save_dir='models'):
        logger.info("[INFO] Carregando modelo YOLOv5 pré-treinado...")
        try:
            self.model = torch.hub.load('ultralytics/yolov5', weights)
            self.save_dir = save_dir
            os.makedirs(save_dir, exist_ok=True)
            logger.info(f"[INFO] Modelo YOLOv5 carregado com sucesso.")
        except Exception as e:
            logger.error(f"[ERRO] Falha ao carregar o modelo: {str(e)}")
            raise

    def train(self, data_loader, epochs, device):
        logger.info("[INFO] Iniciando treinamento...")
        try:
            for epoch in range(epochs):
                logger.info(f"[INFO] Iniciando epoch {epoch + 1}/{epochs}...")
                for batch_idx, (images, targets) in enumerate(data_loader):
                    images = [img.to(device) for img in images]
                    if batch_idx % 100 == 0:
                        logger.info(
                            f"Processando batch {batch_idx}/{len(data_loader)}")

                # Salvar modelo a cada época
                self.save_model(f'model_epoch_{epoch+1}.pt')

            # Salvar modelo final
            self.save_model('model_final.pt')

        except Exception as e:
            logger.error(f"[ERRO] Erro durante o treinamento: {str(e)}")
            raise

    def save_model(self, filename):
        """Salva o modelo treinado"""
        save_path = os.path.join(self.save_dir, filename)
        try:
            # Corrigido: Salvar o estado do modelo
            torch.save({
                'model_state_dict': self.model.state_dict(),
                'class_mapping': class_mapping
            }, save_path)
            logger.info(f"[INFO] Modelo salvo em {save_path}")
        except Exception as e:
            logger.error(f"[ERRO] Falha ao salvar o modelo: {str(e)}")
            raise

    def load_model(self, filename):
        """Carrega um modelo salvo"""
        load_path = os.path.join(self.save_dir, filename)
        try:
            checkpoint = torch.load(load_path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            logger.info(f"[INFO] Modelo carregado de {load_path}")
        except Exception as e:
            logger.error(f"[ERRO] Falha ao carregar o modelo: {str(e)}")
            raise

    def predict(self, image):
        """Realiza predições em uma imagem"""
        try:
            results = self.model(image)
            pred = results.pandas().xyxy[0]
            return pred.values
        except Exception as e:
            logger.error(f"[ERRO] Erro durante a previsão: {str(e)}")
            raise


def visualize_prediction_and_save(image, predictions, output_path, img_name):
    try:
        logger.info("[INFO] Visualizando previsões e salvando a imagem...")

        if torch.is_tensor(image):
            image = image.cpu().numpy()

        if image.max() <= 1.0:
            image = (image * 255).astype(np.uint8)

        if image.shape[0] == 3:
            image = np.transpose(image, (1, 2, 0))

        plt.figure(figsize=(12, 8))
        plt.imshow(image)
        plt.axis('off')

        rev_class_mapping = {v: k for k, v in class_mapping.items()}

        for pred in predictions:
            box = pred[:4]
            conf = pred[4]
            class_id = int(pred[5]) if len(pred) > 5 else -1

            label = rev_class_mapping.get(class_id, f"Classe {class_id}")

            plt.gca().add_patch(plt.Rectangle(
                (box[0], box[1]),
                box[2] - box[0],
                box[3] - box[1],
                fill=False,
                color='red',
                linewidth=2
            ))

            plt.text(
                box[0],
                box[1] - 5,
                f'{label} {conf:.2f}',
                bbox=dict(facecolor='red', alpha=0.5),
                color='white',
                fontsize=8
            )

        os.makedirs(output_path, exist_ok=True)
        result_image_path = os.path.join(output_path, f"pred_{img_name}.jpg")
        plt.savefig(result_image_path)
        logger.info(f"[INFO] Imagem salva em {result_image_path}")
        plt.close()
    except Exception as e:
        logger.error(f"[ERRO] Erro ao visualizar e salvar previsões: {str(e)}")
        raise


class Trainer:
    def __init__(self, model, dataset):
        self.model = model
        self.dataset = dataset

    def prepare_data_loaders(self, batch_size):
        try:
            logger.info(
                "[INFO] Dividindo dataset em treino (80%) e teste (20%)...")
            train_size = int(0.8 * len(self.dataset))
            test_size = len(self.dataset) - train_size
            train_dataset, test_dataset = random_split(
                self.dataset, [train_size, test_size])

            train_loader = DataLoader(
                train_dataset,
                batch_size=batch_size,
                shuffle=True,
                collate_fn=lambda x: tuple(zip(*x)),
                num_workers=0
            )

            test_loader = DataLoader(
                test_dataset,
                batch_size=batch_size,
                shuffle=False,
                collate_fn=lambda x: tuple(zip(*x)),
                num_workers=0
            )

            logger.info(f"[INFO] Dados de treino: {train_size} exemplos.")
            logger.info(f"[INFO] Dados de teste: {test_size} exemplos.")
            return train_loader, test_loader
        except Exception as e:
            logger.error(f"[ERRO] Erro ao preparar data loaders: {str(e)}")
            raise

    def train_model(self, epochs, batch_size):
        try:
            device = torch.device(
                'cuda' if torch.cuda.is_available() else 'cpu')
            logger.info(f"[INFO] Usando dispositivo: {device}")

            train_loader, _ = self.prepare_data_loaders(batch_size)
            self.model.train(train_loader, epochs, device)
            logger.info("[INFO] Treinamento concluído!")
        except Exception as e:
            logger.error(
                f"[ERRO] Erro durante o treinamento do modelo: {str(e)}")
            raise

    def test_model(self, test_loader, output_path):
        logger.info("[INFO] Iniciando teste do modelo...")
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.model.eval()

        with torch.no_grad():
            for batch_idx, (images, targets) in enumerate(test_loader):
                try:
                    for img_idx, (image, target) in enumerate(zip(images, targets)):
                        image = image.to(device)
                        predictions = self.model.predict(image)
                        img_name = f"test_img_{batch_idx}_{img_idx}"
                        visualize_prediction_and_save(
                            image, predictions, output_path, img_name)

                        if batch_idx % 10 == 0:
                            logger.info(
                                f"Processado batch {batch_idx}/{len(test_loader)}")

                except Exception as e:
                    logger.error(
                        f"Erro ao processar batch {batch_idx}: {str(e)}")
                    continue


def main():
    try:
        # Definir caminhos
        annotations_file = "E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed-csv\\annotations_corrected.csv"
        img_dir = "E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed"
        output_path = "E:\\APS6\\NeuroVis-o\\backend\\uploads\\resultado_teste"
        models_dir = "E:\\APS6\\NeuroVis-o\\backend\\models"

        # Verificar se os arquivos existem
        if not os.path.exists(annotations_file):
            raise FileNotFoundError(
                f"Arquivo de anotações não encontrado: {annotations_file}")
        if not os.path.exists(img_dir):
            raise FileNotFoundError(
                f"Diretório de imagens não encontrado: {img_dir}")

        # Criar diretórios necessários
        os.makedirs(output_path, exist_ok=True)
        os.makedirs(models_dir, exist_ok=True)

        # Criar o dataset
        transform = T.Compose([
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        dataset = CustomDataset(annotations_file, img_dir, transform=transform)

        # Criar e treinar o modelo
        model = YOLOModel(weights='yolov5s', save_dir=models_dir)
        trainer = Trainer(model, dataset)

        # Treinar modelo
        trainer.train_model(epochs=10, batch_size=2)

        # Testar modelo
        _, test_loader = trainer.prepare_data_loaders(batch_size=1)
        trainer.test_model(test_loader, output_path)

    except Exception as e:
        logger.error(f"[ERRO] Erro na execução principal: {str(e)}")
        raise


if __name__ == '__main__':
    main()

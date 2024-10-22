import torch
from torch.utils.data import Dataset, DataLoader, random_split
import torchvision.transforms as T
import pandas as pd
import cv2
import os
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import numpy as np
import matplotlib.pyplot as plt

# Verificar a disponibilidade de GPU
print(torch.version.cuda)
print("CUDA disponível:", torch.cuda.is_available())
print("Número de GPUs disponíveis:", torch.cuda.device_count())
if torch.cuda.is_available():
    print("Nome da GPU:", torch.cuda.get_device_name(0))
else:
    print("Nenhuma GPU detectada")


# Classe para carregar o dataset personalizado
class CustomDataset(Dataset):
    def __init__(self, annotations_file, img_dir, transform=None):
        print("[INFO] Carregando anotações e preparando dataset...")
        self.annotations = pd.read_csv(annotations_file, encoding='latin-1')
        self.img_dir = img_dir
        self.transform = transform
        print(
            f"[INFO] Dataset carregado com {len(self.annotations)} exemplos.")

    def __len__(self):
        return len(self.annotations)

    def __getitem__(self, idx):
        img_name = os.path.join(self.img_dir, self.annotations.iloc[idx, 0])
        image = cv2.imread(img_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Coletar as coordenadas da bounding box
        boxes = self.annotations.iloc[idx, 1:5].values.astype(
            np.float32).reshape(-1, 4)

        # Pegar o label e converter para um número
        label = self.annotations.iloc[idx, 5]
        label_num = class_mapping[label]  # Mapeamento de classe

        target = {
            "boxes": torch.tensor(boxes, dtype=torch.float32),
            "labels": torch.tensor([label_num], dtype=torch.int64)
        }

        if self.transform:
            image = self.transform(image)

        return image, target


# Classe para o modelo Faster R-CNN
class FasterRCNNModel:
    def __init__(self, num_classes):
        print("[INFO] Carregando modelo Faster R-CNN pré-treinado...")
        self.model = fasterrcnn_resnet50_fpn(weights="DEFAULT")

        # Alterar o número de classes na camada final de predição
        in_features = self.model.roi_heads.box_predictor.cls_score.in_features
        self.model.roi_heads.box_predictor = FastRCNNPredictor(
            in_features, num_classes)
        print(f"[INFO] Modelo preparado para {num_classes} classes.")

    def train(self, data_loader, num_epochs, optimizer, device):
        self.model.to(device)
        self.model.train()

        for epoch in range(num_epochs):
            epoch_loss = 0
            print(f"[INFO] Iniciando epoch {epoch + 1}/{num_epochs}...")
            for images, targets in data_loader:
                images = [image.to(device) for image in images]
                targets = [{k: v.to(device) for k, v in t.items()}
                           for t in targets]

                optimizer.zero_grad()
                loss_dict = self.model(images, targets)
                losses = sum(loss for loss in loss_dict.values())
                losses.backward()
                optimizer.step()

                epoch_loss += losses.item()

            print(
                f"[INFO] Epoch {epoch + 1} concluída. Loss: {epoch_loss / len(data_loader)}")

        # Salvar o modelo após o treinamento
        torch.save(self.model.state_dict(), 'fasterrcnn_model.pth')
        print("[INFO] Modelo salvo como 'fasterrcnn_model.pth'.")


# Classe para fazer previsões
class Predictor:
    def __init__(self, model):
        self.model = model

    def predict(self, image):
        self.model.eval()
        with torch.no_grad():
            print("[INFO] Realizando previsão na imagem...")
            prediction = self.model([image])
        return prediction

    def visualize_prediction(self, image, prediction):
        boxes = prediction[0]['boxes'].cpu().numpy()
        labels = prediction[0]['labels'].cpu().numpy()
        scores = prediction[0]['scores'].cpu().numpy()

        print("[INFO] Visualizando previsões...")
        plt.imshow(image)
        plt.axis('off')
        for i in range(len(boxes)):
            if scores[i] > 0.5:  # Apenas mostrar caixas com alta confiança
                box = boxes[i]
                plt.gca().add_patch(plt.Rectangle(
                    (box[0], box[1]), box[2] - box[0], box[3] - box[1],
                    fill=False, color='red', linewidth=2))
                plt.text(box[0], box[1], f'Label: {labels[i]}', color='red')
        plt.show()


# Classe para gerenciar o treinamento do modelo
class Trainer:
    def __init__(self, model, dataset):
        self.model = model
        self.dataset = dataset

    def prepare_data_loaders(self, batch_size):
        print("[INFO] Dividindo dataset em treino (80%) e teste (20%)...")
        train_size = int(0.8 * len(self.dataset))
        test_size = len(self.dataset) - train_size
        train_dataset, test_dataset = random_split(
            self.dataset, [train_size, test_size])

        train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True, collate_fn=lambda x: tuple(zip(*x)))
        test_loader = DataLoader(test_dataset, batch_size=batch_size,
                                 shuffle=False, collate_fn=lambda x: tuple(zip(*x)))

        print(f"[INFO] Dados de treino: {train_size} exemplos.")
        print(f"[INFO] Dados de teste: {test_size} exemplos.")
        return train_loader, test_loader

    def train_model(self, num_epochs, batch_size, learning_rate):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"[INFO] Usando dispositivo: {device}")

        train_loader, _ = self.prepare_data_loaders(batch_size)
        optimizer = torch.optim.SGD(self.model.model.parameters(
        ), lr=learning_rate, momentum=0.9, weight_decay=0.0005)

        print("[INFO] Iniciando treinamento...")
        self.model.train(train_loader, num_epochs, optimizer, device)
        print("[INFO] Treinamento concluído!")


# Função para carregar um modelo salvo
def load_model(path, num_classes):
    print(f"[INFO] Carregando modelo de {path}...")
    model = fasterrcnn_resnet50_fpn(weights="DEFAULT")
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    model.load_state_dict(torch.load(path))
    model.eval()
    print("[INFO] Modelo carregado com sucesso.")
    return model


# Função principal para treinamento e previsão
def main():
    annotations_file = "E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed-csv\\annotations_corrected.csv"
    img_dir = "E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed"

    global class_mapping
    class_mapping = {
        'furadeira': 1, 'Guindaste': 2, 'Lixadeira': 3, 'Madeira': 4,
        'Marreta': 5, 'Capacete': 6, 'Pessoa': 7, 'Máscara': 8, 'Colete de Segurança': 9,
        'Máquinas': 10, 'Cone de Segurança': 11, 'Veículo': 12, 'Pá': 13, 'Parafusadeira': 14,
        'Armário': 15, 'Recipiente de resíduos': 16, 'Ferramenta': 17, 'Porta': 18, 'Castelo': 19,
        'Cadeira': 20, 'Faca': 21, 'Saco plástico': 22, 'Casa': 23, 'Luva': 24, 'Janela': 25,
        'Pia': 26, 'Lâmpada': 27, 'Arranha-céu': 28, 'Chave de fenda': 29, 'Edifício de escritório': 30,
        'Caneta': 31, 'Ventilador mecânico': 32, 'Maçaneta': 33, 'Caminhão': 34, 'Tesoura': 35,
        'Ventilador de teto': 36, 'Bota': 37, 'Prego': 38, 'Edifício': 39, 'Martelo': 40,
        'Calculadora': 41, 'Serra elétrica': 42, 'Telha': 43, 'Tinta': 44
    }

    num_classes = len(class_mapping) + 1  # Incluindo a classe background

    # Criar o dataset
    dataset = CustomDataset(annotations_file, img_dir,
                            transform=T.Compose([T.ToTensor()]))

    # Criar o modelo
    model = FasterRCNNModel(num_classes)

    # Criar o trainer
    trainer = Trainer(model, dataset)

    # Treinar o modelo
    trainer.train_model(num_epochs=10, batch_size=2, learning_rate=0.005)

    # Fazer previsões em uma nova imagem
    sample_image_path = "E:\\APS6\\NeuroVis-o\\backend\\uploads\\treino-img\\Brita-90.jpg"
    image = cv2.imread(sample_image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    transform = T.Compose([T.ToTensor()])
    image_tensor = transform(image)

    # Carregar modelo treinado e fazer previsão
    model = load_model('fasterrcnn_model.pth', num_classes)
    predictor = Predictor(model)
    prediction = predictor.predict(image_tensor)
    predictor.visualize_prediction(image, prediction)


if __name__ == '__main__':
    main()

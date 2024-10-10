import torch
import torchvision
from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.rpn import AnchorGenerator
from torchvision.transforms import functional as F
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import os
from PIL import Image

# Classe para o seu dataset personalizado


class CustomDataset(Dataset):
    def __init__(self, img_dir, annotations_file):
        self.img_dir = img_dir
        self.annotations = pd.read_csv(annotations_file)
        self.imgs = os.listdir(img_dir)

    def __len__(self):
        return len(self.imgs)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.imgs[idx])
        image = Image.open(img_path).convert("RGB")

        # Carregar as anotações para a imagem
        annotations = self.annotations[self.annotations['filename']
                                       == self.imgs[idx]]

        boxes = []
        labels = []
        for _, row in annotations.iterrows():
            boxes.append([row['xmin'], row['ymin'], row['xmax'], row['ymax']])
            labels.append(row['class_id'])  # O ID da classe deve estar no CSV

        # Convertendo listas para tensores
        boxes = torch.tensor(boxes, dtype=torch.float32)
        labels = torch.tensor(labels, dtype=torch.int64)

        target = {"boxes": boxes, "labels": labels}

        return F.to_tensor(image), target

# Função para treinar o modelo


def train_faster_rcnn(img_dir, annotations_file, num_classes):
    # Criar o modelo Faster R-CNN
    backbone = torchvision.models.mobilenet_v2(pretrained=True).features
    anchor_generator = AnchorGenerator(
        sizes=((32, 64, 128, 256, 512),), aspect_ratios=((0.5, 1.0, 2.0),) * 5)

    model = FasterRCNN(backbone, num_classes=num_classes,
                       rpn_anchor_generator=anchor_generator)

    # Configuração do dispositivo
    device = torch.device(
        'cuda') if torch.cuda.is_available() else torch.device('cpu')
    model.to(device)

    # Preparar o dataset e o DataLoader
    dataset = CustomDataset(img_dir, annotations_file)
    data_loader = DataLoader(dataset, batch_size=2,
                             shuffle=True, num_workers=4)

    # Definindo o otimizador
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(
        params, lr=0.005, momentum=0.9, weight_decay=0.0005)

    # Treinamento
    num_epochs = 10
    for epoch in range(num_epochs):
        model.train()
        for images, targets in data_loader:
            images = list(image.to(device) for image in images)
            targets = [{k: v.to(device) for k, v in t.items()}
                       for t in targets]

            loss_dict = model(images, targets)
            losses = sum(loss for loss in loss_dict.values())

            optimizer.zero_grad()
            losses.backward()
            optimizer.step()

        print(f"Epoch: {epoch + 1}, Loss: {losses.item()}")


# Parâmetros do treinamento
img_dir = r"E:\APS6\OIDv4_ToolKit\OID\Dataset\train"
annotations_file = r"E:\APS6\OIDv4_ToolKit\OID\csv_folder\train-annotations-bbox.csv"
# +1 para a classe "fundo"
num_classes = len(pd.read_csv(
    r"E:\APS6\OIDv4_ToolKit\OID\csv_folder\class-descriptions-boxable.csv")) + 1

# Executar o treinamento
train_faster_rcnn(img_dir, annotations_file, num_classes)

import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import torchvision.models as models
from torchvision.datasets import CocoDetection
from torch.utils.data import DataLoader
from torchvision.ops import MultiScaleRoIAlign
from tqdm import tqdm


class FastRCNN(nn.Module):
    def __init__(self, num_classes):
        super(FastRCNN, self).__init__()
        self.backbone = models.resnet50(pretrained=True)
        # Remove a camada de classificação
        self.backbone = nn.Sequential(*(list(self.backbone.children())[:-2]))

        self.roi_pool = MultiScaleRoIAlign(
            featmap_names=['0'], output_size=7, sampling_ratio=2)

        # Camadas totalmente conectadas para a classificação
        self.fc1 = nn.Linear(2048 * 7 * 7, 1024)
        self.fc2 = nn.Linear(1024, num_classes)

        # Camadas para a regressão dos bounding boxes
        self.bbox_fc1 = nn.Linear(2048 * 7 * 7, 1024)
        # 4 valores para a caixa delimitadora
        self.bbox_fc2 = nn.Linear(1024, 4)

    def forward(self, images, boxes):
        features = self.backbone(images)
        pooled_features = self.roi_pool(features, boxes)

        pooled_features_flat = pooled_features.view(
            pooled_features.size(0), -1)  # Flatten
        class_logits = self.fc1(pooled_features_flat)
        class_logits = self.fc2(class_logits)

        bbox_regression = self.bbox_fc1(pooled_features_flat)
        bbox_regression = self.bbox_fc2(bbox_regression)

        return class_logits, bbox_regression


def train_fast_rcnn(model, train_loader, criterion, optimizer, num_epochs=10, device='cpu'):
    model.train()
    for epoch in range(num_epochs):
        total_loss = 0
        for images, targets in tqdm(train_loader):
            images = images.to(device)
            # Certifique-se de que 'boxes' está no formato certo
            boxes = targets['boxes'].to(device)
            labels = targets['labels'].to(device)

            optimizer.zero_grad()
            class_logits, bbox_regression = model(images, boxes)

            loss_class = criterion(class_logits, labels)
            # Ajuste para a forma correta
            loss_bbox = criterion(bbox_regression, boxes.view(-1, 4))
            loss = loss_class + loss_bbox
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(
            f'Epoch [{epoch + 1}/{num_epochs}], Loss: {total_loss / len(train_loader):.4f}')


def test_fast_rcnn(model, test_loader, device='cpu'):
    model.eval()
    with torch.no_grad():
        for images, targets in tqdm(test_loader):
            images = images.to(device)
            boxes = targets['boxes'].to(device)
            labels = targets['labels'].to(device)

            class_logits, bbox_regression = model(images, boxes)
            # Implementar sua lógica de teste e visualização aqui


# Inicialização do modelo, critério e otimizador
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
num_classes = 21  # Exemplo para COCO (20 classes + background)
model = FastRCNN(num_classes).to(device)

criterion = nn.CrossEntropyLoss()  # ou outro critério adequado
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Carregamento dos dados
transform = transforms.Compose([
    transforms.Resize((800, 800)),
    transforms.ToTensor()
])

# Carregando o dataset COCO (substitua pelo seu conjunto de dados)
train_dataset = CocoDetection(root='path/to/train/images',
                              annFile='path/to/annotations/train.json', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=4,
                          shuffle=True, num_workers=4)

test_dataset = CocoDetection(root='path/to/test/images',
                             annFile='path/to/annotations/test.json', transform=transform)
test_loader = DataLoader(test_dataset, batch_size=4,
                         shuffle=False, num_workers=4)

# Iniciar o treinamento
train_fast_rcnn(model, train_loader, criterion,
                optimizer, num_epochs=10, device=device)

# Testar o modelo
test_fast_rcnn(model, test_loader, device=device)

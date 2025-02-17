import os
import cv2
import matplotlib.pyplot as plt

# Caminho para o diretório das imagens e os arquivos de anotações
images_dir = r"E:\APS6\NeuroVis-o\backend\uploads\processed"
labels_dir = r"E:\APS6\NeuroVis-o\backend\uploads\yolo_labels"

# Definir tamanho fixo das imagens
IMG_WIDTH = 640
IMG_HEIGHT = 640

# Dicionário de classes fornecido
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

# Função para exibir as imagens com os bounding boxes e as classes


def display_images_with_bboxes():
    for label_file in os.listdir(labels_dir):
        if label_file.endswith(".txt"):
            # Nome da imagem e caminho para o arquivo de imagem
            image_name = label_file.replace(".txt", ".jpg")
            image_path = os.path.join(images_dir, image_name)

            if not os.path.exists(image_path):
                print(f"Imagem {image_name} não encontrada. Pulando...")
                continue

            # Caminho do arquivo de anotação
            label_path = os.path.join(labels_dir, label_file)
            if not os.path.exists(label_path):
                print(
                    f"Arquivo de anotação {label_file} não encontrado. Pulando...")
                continue

            # Carregar a imagem
            img = cv2.imread(image_path)
            # Converter BGR para RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Ler o arquivo de anotações
            with open(label_path, "r") as f:
                for line in f:
                    # Parsing da linha (classe, x_center, y_center, width, height)
                    parts = line.strip().split()
                    class_id = int(parts[0])
                    x_center, y_center, width, height = map(float, parts[1:])

                    # Calcular as coordenadas do bounding box
                    xmin = int((x_center - width / 2) * IMG_WIDTH)
                    ymin = int((y_center - height / 2) * IMG_HEIGHT)
                    xmax = int((x_center + width / 2) * IMG_WIDTH)
                    ymax = int((y_center + height / 2) * IMG_HEIGHT)

                    # Obter o nome da classe
                    class_name = [
                        name for name, id in class_mapping.items() if id == class_id][0]

                    # Desenhar o bounding box e o nome da classe
                    cv2.rectangle(img, (xmin, ymin),
                                  (xmax, ymax), (0, 255, 0), 2)
                    cv2.putText(img, class_name, (xmin, ymin - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Exibir a imagem com Matplotlib
            plt.figure(figsize=(10, 10))
            plt.imshow(img)
            plt.axis('off')  # Não exibir eixos
            plt.show()


# Chamar a função para exibir as imagens
display_images_with_bboxes()

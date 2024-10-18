import os
import pandas as pd
import cv2
from pathlib import Path
from preprocessing import ImageProcessor


class UploadingImageLabel:
    def __init__(self, images_dir, labels_csv, processed_images_dir, processed_csv_dir):
        self.images_dir = images_dir
        self.labels_csv = labels_csv
        self.processed_images_dir = processed_images_dir
        self.processed_csv_dir = processed_csv_dir
        self.image_processor = ImageProcessor()

    def process_images(self):
        # Carrega o arquivo CSV com os rótulos
        labels_df = pd.read_csv(self.labels_csv)

        # Cria os diretórios de saída, se não existirem
        Path(self.processed_images_dir).mkdir(parents=True, exist_ok=True)
        Path(self.processed_csv_dir).mkdir(parents=True, exist_ok=True)

        # Lista de novos dados de rótulos
        new_labels = []

        # Conjunto para acompanhar imagens processadas
        processed_images = set()

        total_images = len(labels_df)

        for index, row in labels_df.iterrows():
            image_name = row['image']

            # Verifica se a imagem já foi processada
            if image_name in processed_images:
                print(f"Imagem já processada: {image_name}. Pulando...")
                continue  # Pula para a próxima iteração do loop

            image_path = os.path.join(self.images_dir, image_name)

            # Verifica se a imagem existe
            if os.path.exists(image_path):
                print(
                    f"Processando a imagem: {image_name} ({index + 1}/{total_images})")
                img = cv2.imread(image_path)

                # Verifica se a imagem foi carregada corretamente
                if img is None:
                    print(f"Erro ao carregar a imagem: {image_path}")
                    continue  # Pula para a próxima iteração do loop

                # Processa a imagem
                processed_img = self.image_processor.preprocess_image(img)

                # Salva a imagem processada
                processed_image_path = os.path.join(
                    self.processed_images_dir, image_name)
                cv2.imwrite(processed_image_path, processed_img)

                # Redimensiona as coordenadas
                xmin, ymin, xmax, ymax = row['xmin'], row['ymin'], row['xmax'], row['ymax']
                new_xmin = xmin * (800 / img.shape[1])
                new_ymin = ymin * (800 / img.shape[0])
                new_xmax = xmax * (800 / img.shape[1])
                new_ymax = ymax * (800 / img.shape[0])

                # Adiciona nova linha ao novo DataFrame
                new_labels.append({
                    'image': image_name,
                    'xmin': new_xmin,
                    'ymin': new_ymin,
                    'xmax': new_xmax,
                    'ymax': new_ymax,
                    'label': row['label']
                })

                # Adiciona a imagem ao conjunto de processadas
                processed_images.add(image_name)

            else:
                print(f"Imagem não encontrada: {image_path}")

        # Cria um novo DataFrame com os dados corrigidos
        new_labels_df = pd.DataFrame(new_labels)

        # Salva o novo CSV
        new_csv_path = os.path.join(
            self.processed_csv_dir, 'annotations_corrected.csv')
        new_labels_df.to_csv(new_csv_path, index=False)

        print(f"Imagens processadas e salvas em: {self.processed_images_dir}")
        print(f"Novo CSV salvo em: {new_csv_path}")


# Uso da classe
if __name__ == "__main__":
    images_dir = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\treino-img"
    labels_csv = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\treino-label\\annotations.csv"
    processed_images_dir = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed"
    processed_csv_dir = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed-csv"

    uploader = UploadingImageLabel(
        images_dir, labels_csv, processed_images_dir, processed_csv_dir)
    uploader.process_images()

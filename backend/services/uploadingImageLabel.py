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
        labels_df = pd.read_csv(self.labels_csv, encoding='latin1')
        Path(self.processed_images_dir).mkdir(parents=True, exist_ok=True)
        Path(self.processed_csv_dir).mkdir(parents=True, exist_ok=True)

        new_labels = []
        processed_images = set()

        total_images = len(labels_df)

        for index, row in labels_df.iterrows():
            image_name = row['image']

            if image_name in processed_images:
                print(f"Imagem já processada: {image_name}. Pulando...")
                continue

            image_path = os.path.join(self.images_dir, image_name)

            if os.path.exists(image_path):
                print(
                    f"Processando a imagem: {image_name} ({index + 1}/{total_images})")
                img = cv2.imread(image_path)

                if img is None:
                    print(f"Erro ao carregar a imagem: {image_path}")
                    continue

                processed_img = self.image_processor.preprocess_image(img)

                processed_image_path = os.path.join(
                    self.processed_images_dir, image_name)
                cv2.imwrite(processed_image_path, processed_img)

                original_height, original_width = img.shape[:2]
                new_height, new_width = 800, 800

                # Se a imagem é menor que 800x800
                if original_height < 800 and original_width < 800:
                    # Calcule os offsets
                    y_offset = (new_height - original_height) // 2
                    x_offset = (new_width - original_width) // 2

                    # Ajuste as coordenadas de acordo com os offsets
                    xmin, ymin, xmax, ymax = row['xmin'], row['ymin'], row['xmax'], row['ymax']
                    new_xmin = xmin + x_offset
                    new_ymin = ymin + y_offset
                    new_xmax = xmax + x_offset
                    new_ymax = ymax + y_offset
                else:
                    # Se a imagem é maior ou igual a 800x800, redimensione as coordenadas proporcionalmente
                    new_xmin = row['xmin'] * (new_width / original_width)
                    new_ymin = row['ymin'] * (new_height / original_height)
                    new_xmax = row['xmax'] * (new_width / original_width)
                    new_ymax = row['ymax'] * (new_height / original_height)

                new_labels.append({
                    'image': image_name,
                    'xmin': new_xmin,
                    'ymin': new_ymin,
                    'xmax': new_xmax,
                    'ymax': new_ymax,
                    'label': row['label']
                })

                processed_images.add(image_name)

            else:
                print(f"Imagem não encontrada: {image_path}")

        new_labels_df = pd.DataFrame(new_labels)
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

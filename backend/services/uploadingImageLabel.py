import os
import pandas as pd
import cv2
from pathlib import Path
from preprocessing import ImageProcessor


class UploadingImageLabel:
    def __init__(self, images_dir, labels_csv, processed_images_dir, processed_csv_dir, cache_size=100):
        self.images_dir = images_dir
        self.labels_csv = labels_csv
        self.processed_images_dir = processed_images_dir
        self.processed_csv_dir = processed_csv_dir
        self.image_processor = ImageProcessor()
        self.image_cache = {}  # Cache para armazenar imagens processadas
        self.cache_size = cache_size  # Define o tamanho do cache

    def process_images(self):
        try:
            # Tenta abrir o CSV com 'utf-8' ou 'latin1'
            try:
                labels_df = pd.read_csv(self.labels_csv, encoding='utf-8')
            except UnicodeDecodeError:
                labels_df = pd.read_csv(self.labels_csv, encoding='latin1')
        except Exception as e:
            print(f"Erro ao ler o CSV de labels: {e}")
            return

        Path(self.processed_images_dir).mkdir(parents=True, exist_ok=True)
        Path(self.processed_csv_dir).mkdir(parents=True, exist_ok=True)

        new_labels = []
        processed_images = set()  # Set para controlar imagens já processadas
        total_images = len(labels_df)

        for index, row in labels_df.iterrows():
            try:
                image_name = row['image']

                # Verifica se a imagem já foi processada
                if image_name not in processed_images:
                    image_path = os.path.join(self.images_dir, image_name)

                    if not os.path.exists(image_path):
                        print(f"Imagem não encontrada: {image_path}")
                        continue

                    # Processa a imagem apenas uma vez
                    print(
                        f"Processando a imagem: {image_name} ({index + 1}/{total_images})")
                    img = cv2.imread(image_path)

                    if img is None:
                        print(f"Erro ao carregar a imagem: {image_path}")
                        continue

                    # Processa a imagem
                    processed_img = self.image_processor.preprocess_image(img)
                    processed_image_path = os.path.join(
                        self.processed_images_dir, image_name)
                    cv2.imwrite(processed_image_path, processed_img)

                    # Armazena a imagem no cache
                    self.image_cache[image_name] = img
                    processed_images.add(image_name)

                # Aqui garantimos que todos os labels para a mesma imagem sejam processados
                original_height, original_width = img.shape[:2]
                new_height, new_width = 800, 800

                # Se a imagem é menor que 800x800
                if original_height < 800 and original_width < 800:
                    y_offset = (new_height - original_height) // 2
                    x_offset = (new_width - original_width) // 2

                    xmin, ymin, xmax, ymax = row['xmin'], row['ymin'], row['xmax'], row['ymax']
                    new_xmin = xmin + x_offset
                    new_ymin = ymin + y_offset
                    new_xmax = xmax + x_offset
                    new_ymax = ymax + y_offset
                else:
                    # Redimensiona proporcionalmente
                    new_xmin = row['xmin'] * (new_width / original_width)
                    new_ymin = row['ymin'] * (new_height / original_height)
                    new_xmax = row['xmax'] * (new_width / original_width)
                    new_ymax = row['ymax'] * (new_height / original_height)

                # Adiciona as anotações corrigidas
                new_labels.append({
                    'image': image_name,
                    'xmin': new_xmin,
                    'ymin': new_ymin,
                    'xmax': new_xmax,
                    'ymax': new_ymax,
                    'label': row['label']
                })

                # Limpa o cache quando atingir o limite para economizar memória
                if len(self.image_cache) >= self.cache_size:
                    self.image_cache.clear()
                    print(
                        f"Cache esvaziado após processar {len(processed_images)} imagens.")

            except Exception as e:
                print(f"Erro ao processar a imagem {image_name}: {e}")
                continue

        # Salvando o novo CSV com as labels corrigidas
        try:
            new_labels_df = pd.DataFrame(new_labels)
            new_csv_path = os.path.join(
                self.processed_csv_dir, 'annotations_corrected.csv')
            # Salva com a codificação utf-8 para garantir os caracteres especiais
            new_labels_df.to_csv(new_csv_path, index=False,
                                 encoding='utf-8-sig')
            print(f"Novo CSV salvo em: {new_csv_path}")
        except Exception as e:
            print(f"Erro ao salvar o novo CSV: {e}")

        print("Processamento concluído.")


# Uso da classe
if __name__ == "__main__":
    images_dir = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\treino-img"
    labels_csv = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\treino-label\\annotations.csv"
    processed_images_dir = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed"
    processed_csv_dir = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed-csv"

    uploader = UploadingImageLabel(
        images_dir, labels_csv, processed_images_dir, processed_csv_dir, cache_size=100)

    uploader.process_images()

import os
import cv2
import pandas as pd

# Diretórios
processed_image_dir = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed"
annotations_csv_path = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed-csv\\annotations_corrected.csv"


def load_annotations_from_csv(csv_path):
    # Tentar diferentes codificações
    for encoding in ['utf-8', 'ISO-8859-1', 'cp1252']:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"Successfully read CSV file with encoding: {encoding}")
            return df
        except Exception as e:
            print(f"Failed with encoding {encoding}: {e}")
    return None


def draw_annotations(image, annotations):
    for _, annotation in annotations.iterrows():
        # Desenhar retângulo em torno do objeto
        cv2.rectangle(image, (int(annotation['xmin']), int(annotation['ymin'])),
                      (int(annotation['xmax']), int(annotation['ymax'])), (0, 255, 0), 2)
        # Colocar o texto da classe acima do retângulo
        cv2.putText(image, annotation['label'], (int(annotation['xmin']), int(annotation['ymin']) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def visualize_images(annotations):
    for _, annotation in annotations.iterrows():
        img_filename = annotation['image']
        img_path = os.path.join(processed_image_dir, img_filename)

        # Carregar a imagem
        image = cv2.imread(img_path)
        if image is None:
            print(f"Error loading image: {img_path}")
            continue

        # Criar um DataFrame com as anotações correspondentes à imagem
        img_annotations = annotations[annotations['image'] == img_filename]

        # Desenhar as anotações na imagem
        draw_annotations(image, img_annotations)

        # Mostrar a imagem com as anotações
        cv2.imshow(f'Annotated Image: {img_filename}', image)

        # Aguarde até que uma tecla seja pressionada
        key = cv2.waitKey(0)
        if key == 27:  # Pressione ESC para sair
            break

    # Fechar todas as janelas após exibir todas as imagens
    cv2.destroyAllWindows()


if __name__ == "__main__":
    annotations = load_annotations_from_csv(annotations_csv_path)
    if annotations is not None:
        visualize_images(annotations)

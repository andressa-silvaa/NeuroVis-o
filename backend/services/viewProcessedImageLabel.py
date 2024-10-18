import os
import cv2

# Diretórios
processed_image_dir = r"E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed"


def load_annotations(annotation_path):
    annotations = []

    # Verifique se o arquivo de anotações existe
    if not os.path.exists(annotation_path):
        print(f"Annotation file not found: {annotation_path}")
        return annotations

    with open(annotation_path, 'r') as f:
        for line in f.readlines():
            parts = line.strip().split(' ')
            if len(parts) >= 5:
                class_name = parts[0]  # Nome da classe
                try:
                    # Ler coordenadas como floats
                    x_min = float(parts[1])
                    y_min = float(parts[2])
                    x_max = float(parts[3])
                    y_max = float(parts[4])

                    # Adicionar as coordenadas já na escala de pixels
                    annotations.append({
                        'LabelName': class_name,
                        'XMin': int(x_min),
                        'YMin': int(y_min),
                        'XMax': int(x_max),
                        'YMax': int(y_max)
                    })
                except ValueError as e:
                    print(f"Error parsing line: {line.strip()} - {e}")
            else:
                print(f"Invalid annotation line: {line.strip()}")

    return annotations


def draw_annotations(image, annotations):
    for annotation in annotations:
        # Desenhar retângulo em torno do objeto
        cv2.rectangle(image, (annotation['XMin'], annotation['YMin']),
                      (annotation['XMax'], annotation['YMax']), (0, 255, 0), 2)
        # Opcional: colocar o texto da classe acima do retângulo
        cv2.putText(image, annotation['LabelName'], (annotation['XMin'], annotation['YMin'] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def visualize_images():
    for filename in os.listdir(processed_image_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            img_path = os.path.join(processed_image_dir, filename)
            annotation_path = img_path.replace(filename.split('.')[-1], 'txt')

            # Carregar a imagem
            image = cv2.imread(img_path)
            if image is None:
                print(f"Error loading image: {img_path}")
                continue

            # Carregar as anotações
            annotations = load_annotations(annotation_path)
            if not annotations:
                print(f"No annotations found for {filename}")
                continue

            # Desenhar as anotações na imagem
            draw_annotations(image, annotations)

            # Mostrar a imagem com as anotações
            cv2.imshow(f'Annotated Image: {filename}', image)

            # Aguarde até que uma tecla seja pressionada
            key = cv2.waitKey(0)
            if key == 27:  # Pressione ESC para sair
                break

    # Fechar todas as janelas após exibir todas as imagens
    cv2.destroyAllWindows()


if __name__ == "__main__":
    visualize_images()

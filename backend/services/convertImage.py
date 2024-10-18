import os
from PIL import Image


def convert_images_to_jpg(directory):
    # Verifica se o diretório existe
    if not os.path.exists(directory):
        print(f"O diretório {directory} não existe.")
        return

    # Itera sobre todos os arquivos no diretório
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            file_path = os.path.join(directory, filename)
            try:
                with Image.open(file_path) as img:
                    # Converte a imagem para RGB
                    rgb_img = img.convert('RGB')
                    # Define o novo nome do arquivo
                    new_filename = os.path.splitext(filename)[0] + '.jpg'
                    new_file_path = os.path.join(directory, new_filename)
                    # Salva a imagem como JPG
                    rgb_img.save(new_file_path, 'JPEG')
                    print(f"Convertido: {new_file_path}")
            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")


if __name__ == "__main__":
    # Solicita ao usuário o diretório
    user_directory = input("Digite o caminho do diretório com as imagens: ")
    convert_images_to_jpg(user_directory)

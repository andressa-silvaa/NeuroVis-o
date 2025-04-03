import os
import glob


def process_txt_files(directory):
    # Muda para o diretório fornecido
    os.chdir(directory)
    # Busca todos os arquivos .txt
    txt_files = glob.glob("*.txt")

    for txt_file in txt_files:
        # Nome da imagem correspondente
        image_name = os.path.splitext(txt_file)[0] + '.jpg'
        formatted_lines = []

        # Lê o conteúdo do arquivo .txt
        with open(txt_file, 'r') as file:
            lines = file.readlines()

        for line in lines:
            parts = line.strip().split()  # Divide a linha em partes

            # O label é o primeiro elemento até o índice onde os números começam (últimos 4 elementos são coordenadas)
            # Juntar tudo antes dos 4 últimos elementos como o label
            label = ' '.join(parts[:-4])
            xmin = parts[-4]
            ymin = parts[-3]
            xmax = parts[-2]
            ymax = parts[-1]

            # Formata a linha corretamente (image,xmin,ymin,xmax,ymax,label)
            formatted_line = f"{image_name},{xmin} {ymin} {xmax} {ymax},{label}"
            formatted_lines.append(formatted_line)

        # Grava o arquivo apenas se houver linhas formatadas
        if formatted_lines:
            with open(txt_file, 'w') as outfile:
                outfile.write('\n'.join(formatted_lines) + '\n')
        else:
            print(
                f"Aviso: O arquivo {txt_file} não contém linhas válidas para formatar e não foi modificado.")


# Pede ao usuário para inserir o diretório
user_directory = input(
    "Digite o caminho do diretório contendo os arquivos .txt: ")
# Chama a função com o diretório fornecido pelo usuário
process_txt_files(user_directory)

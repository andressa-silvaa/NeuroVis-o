import os
import pandas as pd
import unicodedata

# Função para normalizar texto


def normalize_text(text):
    return unicodedata.normalize('NFKD', text)

# Função para ler arquivos TXT e extrair dados


def read_txt_files(directory):
    data = []

    # Itera sobre todos os arquivos no diretório
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        line = line.strip()  # Remove espaços em branco
                        if line:  # Verifica se a linha não está vazia
                            parts = line.split(',')
                            if len(parts) == 6:  # Verifica se a linha contém 6 partes
                                # Captura o nome da imagem corretamente
                                image_name = parts[0].strip()  # Nome da imagem
                                # Normaliza o label para evitar problemas de caracteres
                                label = normalize_text(parts[5].strip())
                                # Adiciona a linha formatada à lista
                                data.append([image_name] + [float(coord.strip())
                                            for coord in parts[1:5]] + [label])
                            else:
                                print(
                                    f"Linha com formato inesperado em {filename}: {line}")
            except UnicodeDecodeError:
                # Tenta abrir com uma codificação alternativa se UTF-8 falhar
                try:
                    with open(file_path, 'r', encoding='ISO-8859-1') as file:
                        for line in file:
                            line = line.strip()
                            if line:
                                parts = line.split(',')
                                if len(parts) == 6:
                                    # Nome da imagem
                                    image_name = parts[0].strip()
                                    label = normalize_text(parts[5].strip())
                                    data.append([image_name] + [float(coord.strip())
                                                for coord in parts[1:5]] + [label])
                                else:
                                    print(
                                        f"Linha com formato inesperado em {filename}: {line}")
                except Exception as e:
                    print(f"Erro ao ler o arquivo {filename}: {e}")

    return data

# Função principal


def main():
    directory = input(
        "Por favor, insira o diretório onde os arquivos TXT estão localizados: ")

    if not os.path.isdir(directory):
        print("O diretório informado não é válido.")
        return

    # Lê os arquivos TXT e extrai os dados
    data = read_txt_files(directory)

    # Verifica se dados foram encontrados
    if not data:
        print("Nenhum dado foi encontrado nos arquivos TXT.")
        return

    # Cria um DataFrame do pandas a partir dos dados
    df = pd.DataFrame(
        data, columns=['image', 'xmin', 'ymin', 'xmax', 'ymax', 'label'])

    # Salva os dados em um arquivo CSV
    output_csv = os.path.join(directory, 'output.csv')
    # Use 'utf-8-sig' para garantir a codificação correta
    df.to_csv(output_csv, index=False, encoding='utf-8-sig')

    print(f"Arquivo CSV criado com sucesso: {output_csv}")


if __name__ == "__main__":
    main()

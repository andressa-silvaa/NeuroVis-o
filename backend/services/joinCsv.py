import os
import pandas as pd

# Função para combinar arquivos CSV


def combine_csv_files(directory):
    # Lista para armazenar os DataFrames
    df_list = []

    # Percorre todos os arquivos no diretório
    for filename in os.listdir(directory):
        # Verifica se o arquivo é um CSV
        if filename.endswith('.csv'):
            # Lê o arquivo CSV e adiciona à lista
            file_path = os.path.join(directory, filename)
            # Usando 'utf-8-sig' para manter caracteres acentuados
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df_list.append(df)

    # Concatena todos os DataFrames em um único DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)

    # Salva o DataFrame combinado em um novo arquivo CSV
    output_file = os.path.join(directory, 'annotations.csv')
    combined_df.to_csv(output_file, index=False,
                       encoding='utf-8-sig')  # Salva com 'utf-8-sig'

    print(f"Arquivo combinado salvo como {output_file}")


# Pede ao usuário para inserir o diretório
directory = input("Insira o diretório onde estão os arquivos CSV: ")
combine_csv_files(directory)

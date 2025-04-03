import pandas as pd

# Caminho para o arquivo CSV
annotations_file = "E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed-csv\\annotations_corrected.csv"

# Carregar o arquivo CSV com uma codificação diferente
df = pd.read_csv(annotations_file, encoding='ISO-8859-1')

# Exibir as primeiras linhas do DataFrame para verificação
print("Antes da filtragem:")
print(df.head())

# Filtrar os registros onde xmin, ymin, xmax, ymax são todos menores ou iguais a 640
filtered_df = df[
    (df['xmin'] <= 640) &
    (df['ymin'] <= 640) &
    (df['xmax'] <= 640) &
    (df['ymax'] <= 640)
]

# Exibir as primeiras linhas do DataFrame filtrado para verificação
print("Depois da filtragem:")
print(filtered_df.head())

# Salvar o DataFrame filtrado em um novo arquivo CSV
filtered_annotations_file = "E:\\APS6\\NeuroVis-o\\backend\\uploads\\processed-csv\\annotations_filtered.csv"
filtered_df.to_csv(filtered_annotations_file, index=False)

print(f"Registros filtrados salvos em: {filtered_annotations_file}")

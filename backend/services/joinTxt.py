import os


def remove_duplicates_from_folder(folder_path):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file.endswith(".txt"):
            with open(file_path, "r") as f:
                lines = f.readlines()

            # Removendo duplicatas
            unique_lines = list(set(lines))

            if len(lines) != len(unique_lines):
                with open(file_path, "w") as f:
                    f.writelines(unique_lines)
                print(f"Duplicatas removidas de: {file}")


# Definindo os caminhos das pastas
dataset_path = "E:/APS6/NeuroVis-o/backend/dataset/labels/"
folders = ["train", "test", "val"]

# Aplicando a função para cada pasta
for folder in folders:
    folder_path = os.path.join(dataset_path, folder)
    remove_duplicates_from_folder(folder_path)

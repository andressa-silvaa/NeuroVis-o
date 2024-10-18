import os
import shutil
import csv


class OrganizarFiles:
    def __init__(self, input_dir, nome_padrao, class_map=None, label_dir=None):
        self.input_dir = input_dir
        self.nome_padrao = nome_padrao
        self.csv_file = os.path.join(self.input_dir, "annotations.csv")
        self.output_dir = os.path.join(self.input_dir, "renomeado")
        os.makedirs(self.output_dir, exist_ok=True)
        self.new_csv_file = os.path.join(
            self.output_dir, "novo_annotations.csv")

        # Para a operação de conversão dos labels
        self.class_map = class_map
        self.label_dir = label_dir

    def renomear_imagens_e_atualizar_csv(self):
        """Renomeia as imagens e atualiza o arquivo CSV."""
        image_counter = 1
        new_rows = []

        if not os.path.exists(self.csv_file):
            print(f"Arquivo CSV não encontrado: {self.csv_file}")
            return

        with open(self.csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            new_rows.append(header)

            for row in reader:
                old_image_name = row[0]
                new_image_name = f"{self.nome_padrao}-{image_counter}.jpeg"

                old_image_path = os.path.join(self.input_dir, old_image_name)
                new_image_path = os.path.join(self.output_dir, new_image_name)

                if os.path.exists(old_image_path):
                    shutil.copy(old_image_path, new_image_path)
                    row[0] = new_image_name  # Atualiza apenas o nome da imagem
                    new_rows.append(row)
                    image_counter += 1
                else:
                    print(f"Imagem não encontrada: {old_image_name}")

        with open(self.new_csv_file, 'w', newline='', encoding='utf-8') as new_csvfile:
            writer = csv.writer(new_csvfile)
            writer.writerows(new_rows)

        print(f"Imagens renomeadas e novo CSV salvo em: {self.output_dir}")

    def convert_coordinates(self, x_center, y_center, width, height, img_width, img_height):
        """Converte coordenadas do formato YOLO para xmin, ymin, xmax, ymax."""
        # Desnormaliza as coordenadas para a escala da imagem
        x_center = x_center * img_width
        y_center = y_center * img_height
        width = width * img_width
        height = height * img_height

        xmin = x_center - (width / 2)
        ymin = y_center - (height / 2)
        xmax = x_center + (width / 2)
        ymax = y_center + (height / 2)
        return xmin, ymin, xmax, ymax

    def process_label_file(self, file_path, img_width, img_height):
        """Processa um arquivo de label, converte e filtra as classes desejadas."""
        image_name = os.path.basename(file_path.replace(
            ".txt", ".jpg"))  # Extrai apenas o nome do arquivo
        new_lines = []

        with open(file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split()
            class_id = parts[0]

            if class_id in self.class_map:
                # Extrair e converter coordenadas
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                xmin, ymin, xmax, ymax = self.convert_coordinates(
                    x_center, y_center, width, height, img_width, img_height)

                # Adicionar nova linha no formato: image,xmin,ymin,xmax,ymax,label
                new_line = f"{image_name},{xmin},{ymin},{xmax},{ymax},{self.class_map[class_id]}"
                new_lines.append(new_line)

        # Salva as novas anotações no arquivo txt
        with open(file_path, 'w') as f:
            for new_line in new_lines:
                f.write(new_line + '\n')

        if not new_lines:
            # Se nenhuma linha foi mantida, deixe o arquivo vazio
            open(file_path, 'w').close()

    def process_all_label_files(self):
        """Processa todos os arquivos de label no diretório."""
        if not os.path.exists(self.label_dir):
            print(f"Diretório de labels não encontrado: {self.label_dir}")
            return

        # Supondo que as imagens têm um tamanho fixo, ou você pode passar isso de forma dinâmica
        img_width = 1920  # Substitua pelo valor real da largura das suas imagens
        img_height = 1080  # Substitua pelo valor real da altura das suas imagens

        for label_file in os.listdir(self.label_dir):
            if label_file.endswith(".txt"):
                file_path = os.path.join(self.label_dir, label_file)
                self.process_label_file(file_path, img_width, img_height)

        print(
            f"Todos os arquivos de label foram processados em: {self.label_dir}")


def main():
    while True:
        print("\nEscolha a operação:")
        print("1 - Renomear imagens e atualizar CSV")
        print("2 - Converter arquivos de label")
        print("0 - Sair")
        choice = input("Digite o número da operação: ")

        if choice == '1':
            input_dir = input(
                "Por favor, insira o caminho completo do diretório com as imagens e o arquivo CSV: ")
            if not os.path.isdir(input_dir):
                print(
                    f"O diretório '{input_dir}' não existe. Tente novamente.")
                continue

            nome_padrao = input(
                "Digite o nome padrão para as imagens (ex: Andaime, Tijolo): ")
            organizador = OrganizarFiles(input_dir, nome_padrao)
            organizador.renomear_imagens_e_atualizar_csv()

        elif choice == '2':
            input_dir = input(
                "Por favor, insira o caminho completo do diretório com as imagens: ")
            label_dir = input(
                "Digite o caminho do diretório de labels (anotações): ")
            if not os.path.isdir(input_dir) or not os.path.isdir(label_dir):
                print(f"Um dos diretórios fornecidos não existe. Tente novamente.")
                continue

            class_map = {
                '0': 'Capacete',
                '1': 'Máscara',
                '5': 'Pessoa',
                '6': 'Cone de Segurança',
                '7': 'Colete de Segurança',
                '8': 'Máquinas',
                '9': 'Veículo'
            }

            organizador = OrganizarFiles(
                input_dir, nome_padrao=None, class_map=class_map, label_dir=label_dir)
            organizador.process_all_label_files()

        elif choice == '0':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()

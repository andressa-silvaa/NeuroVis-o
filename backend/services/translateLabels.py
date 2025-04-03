import os

# Dicionário de traduções
translations = {
    "Ceiling": "Teto",
    "Cabinetry": "Armário",
    "Lamp": "Lâmpada",
    "Plastic": "Plástico",
    "Building": "Edifício",
    "Waste": "Resíduo",
    "Glove": "Luva",
    "Boot": "Bota",
    "Chainsaw": "Serra elétrica",
    "Sink": "Pia",
    "Window": "Janela",
    "Screwdriver": "Chave de fenda",
    "Pen": "Caneta",
    "Knife": "Faca",
    "Truck": "Caminhão",
    "Person": "Pessoa",
    "Nail": "Prego",
    "Door": "Porta",
    "House": "Casa",
    "Castle": "Castelo",
    "Tool": "Ferramenta",
    "Scissors": "Tesoura",
    "Chair": "Cadeira",
    "Office": "Escritório",
    "Mechanical": "Mecânico",
    "Skyscraper": "Arranha-céu",
    "Hammer": "Martelo",
    "Calculator": "Calculadora",
    "Office building": "Edifício de escritório",
    "Door handle": "Maçaneta",
    "Ceiling fan": "Ventilador de teto",
    "Mechanical fan": "Ventilador mecânico",
    "Waste container": "Recipiente de resíduos",
    "Plastic bag": "Saco plástico",
}

# Solicitar diretório ao usuário
directory = input("Digite o caminho do diretório com os arquivos .txt: ")

# Processar cada arquivo no diretório
for filename in os.listdir(directory):
    if filename.endswith(".txt"):
        file_path = os.path.join(directory, filename)

        with open(file_path, 'r') as file:
            lines = file.readlines()

        with open(file_path, 'w') as file:
            for line in lines:
                parts = line.strip().split(',')
                if len(parts) > 1:
                    # Traduzir o rótulo
                    label = parts[-1].strip()
                    # Se não encontrar, mantém o original
                    translated_label = translations.get(label, label)
                    new_line = f"{parts[0]},{parts[1].strip()},{translated_label}\n"
                    file.write(new_line)

print("Tradução concluída com sucesso!")

#!/bin/bash
# Atualiza e instala dependências do sistema
sudo apt-get update
sudo apt-get install -y unixodbc unixodbc-dev unixodbc-bin gnupg2 curl

# Adiciona repositório da Microsoft e instala o driver ODBC
curl https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/ubuntu/20.04/prod focal main" | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools

# Configura variáveis de ambiente para o driver
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc

# Instala dependências do Python
python -m pip install --upgrade pip
python -m pip install gunicorn
python -m pip install -r requirements.txt

# Inicia a aplicação
gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app
#!/bin/bash
# Atualiza pacotes e instala dependências do sistema
sudo apt-get update
sudo apt-get install -y unixodbc unixodbc-dev gnupg2 curl

# Instala o driver ODBC da Microsoft para SQL Server
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Instala dependências do Python
pip install --upgrade pip
pip install -r requirements.txt gunicorn

# Inicia a aplicação com Gunicorn (recomendado para produção)
gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 app:app
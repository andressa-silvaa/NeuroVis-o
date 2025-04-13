
#!/bin/bash
# Script otimizado para instalação no Render

# Instala dependências essenciais
sudo apt-get update
sudo apt-get install -y unixodbc unixodbc-dev gcc g++

# Instala o driver ODBC da Microsoft (versão simplificada para Render)
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Configura variáveis de ambiente essenciais
export PATH="$PATH:/opt/mssql-tools/bin"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/mssql-tools/lib"

# Verifica a instalação do driver
odbcinst -q -d -n "ODBC Driver 17 for SQL Server"

# Instala dependências do Python
pip install --upgrade pip
pip install -r requirements.txt

# Inicia a aplicação
gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app

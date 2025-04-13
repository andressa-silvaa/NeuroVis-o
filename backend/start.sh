#!/bin/bash
# Script otimizado para instalação no Render

# Habilita exibição dos comandos e interrompe em caso de erro
set -ex

echo "===== Iniciando processo de instalação ====="

# Instala dependências essenciais
echo "Instalando pacotes base..."
apt-get update
apt-get install -y unixodbc unixodbc-dev curl gnupg2 apt-transport-https

# Adiciona repositório Microsoft
echo "Adicionando repositório Microsoft..."
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Atualiza pacotes e instala driver
echo "Instalando Microsoft ODBC Driver 17..."
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools

# Verifica a instalação do driver
echo "Verificando instalação do driver ODBC..."
odbcinst -j
odbcinst -q -d
odbcinst -q -d -n "ODBC Driver 17 for SQL Server" || echo "Driver não encontrado na consulta"

# Encontra manualmente os arquivos do driver
echo "Localizando arquivos do driver..."
find / -name "libmsodbcsql*.so*" 2>/dev/null || echo "Arquivos do driver não encontrados"

# Configura variáveis de ambiente
echo "Configurando variáveis de ambiente..."
export PATH="$PATH:/opt/mssql-tools/bin"
export LD_LIBRARY_PATH="/opt/microsoft/msodbcsql17/lib64:$LD_LIBRARY_PATH"

# Verifica se os diretórios existem
ls -la /opt/microsoft/ || echo "Diretório não encontrado"
ls -la /opt/microsoft/msodbcsql17/ || echo "Diretório não encontrado"
ls -la /opt/microsoft/msodbcsql17/lib64/ || echo "Diretório não encontrado"

# Adiciona ao .bashrc para persistir
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH="/opt/microsoft/msodbcsql17/lib64:$LD_LIBRARY_PATH"' >> ~/.bashrc

# Instala dependências Python
echo "Instalando dependências Python..."
pip install --upgrade pip
pip install wheel  # Importante para compilar pacotes
pip install -r requirements.txt

# Cria diretórios necessários
echo "Criando diretórios necessários..."
mkdir -p uploads/images
mkdir -p model_weights

echo "===== Instalação concluída com sucesso! ====="
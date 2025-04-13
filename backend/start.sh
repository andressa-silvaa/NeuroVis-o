#!/bin/bash
# Script otimizado para instalação no Render
set -e  # Para o script se algum comando falhar

echo "===== Iniciando processo de instalação ====="

# Cria diretórios necessários
echo "Criando diretórios necessários..."
mkdir -p uploads/images
mkdir -p model_weights

# Instala dependências Python
echo "Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurar informações de diagnóstico
echo "Configurando ambiente de diagnóstico..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "===== Instalação concluída com sucesso! ====="
# Use uma imagem base compatível com o driver ODBC
FROM python:3.10-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Instala o driver da Microsoft para SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Define o diretório de trabalho
WORKDIR /app

# Copia o projeto
COPY . .

# Instala as dependências do Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe a porta do Render
EXPOSE 10000


CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "4", "app:app"]

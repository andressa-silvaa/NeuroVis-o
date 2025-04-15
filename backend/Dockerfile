FROM python:3.10-slim as builder

# Instala apenas as dependências essenciais do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Cria um usuário não-root para segurança
RUN useradd -m appuser && mkdir /app && chown appuser:appuser /app
USER appuser
WORKDIR /app

# Primeiro copia apenas os requirements para cachear as dependências
COPY --chown=appuser:appuser requirements.txt .

# Instala dependências Python (sem cache para reduzir tamanho)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação
COPY --chown=appuser:appuser . .

# Porta que o Render espera (10000)
EXPOSE 10000

# Configuração otimizada do Gunicorn para o Render:
# --preload: Carrega o app antes de forking workers
# --timeout: Aumentado para 120s
# --workers: 1 worker (adequado para plano básico)
# --access-logfile: Habilita logs de acesso
# --error-logfile: Habilita logs de erro
CMD ["gunicorn", \
    "--bind", "0.0.0.0:10000", \
    "--workers", "1", \
    "--timeout", "120", \
    "--preload", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "app:app"]
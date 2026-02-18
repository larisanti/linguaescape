FROM python:3.13.11

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala dependências do sistema operacional que algumas bibliotecas Python (como fpdf2) podem precisar
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia o requirements.txt primeiro para aproveitar o cache do Docker (evita reinstalar tudo se você não mudou as bibliotecas)
COPY requirements.txt .

# Instala as bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto do código do seu projeto para dentro do contêiner
COPY . .

# Expõe as portas que usaremos (8501 para Streamlit, 8000 para FastAPI)
EXPOSE 8501 8000
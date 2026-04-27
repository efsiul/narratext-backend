# Edge TTS HTTP Server
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
# Actualizar edge-tts a la última versión para evitar problemas conocidos
RUN pip install --no-cache-dir --upgrade \
    edge-tts \
    flask \
    flask-cors

COPY server.py /app/server.py

EXPOSE 5000

CMD ["python", "server.py"]



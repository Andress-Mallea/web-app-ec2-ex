FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Servidor de desarrollo de Flask (sin gunicorn). --reload recarga al guardar;
# --no-debugger evita exponer la consola interactiva de Werkzeug en la red.
CMD ["flask", "--app", "run:app", "run", "--host=0.0.0.0", "--port=8000", "--reload", "--no-debugger"]

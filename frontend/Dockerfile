FROM python:3.12-slim

WORKDIR /site
COPY . .

EXPOSE 8080

# Servidor estático mínimo de Python (sin nginx).
CMD ["python", "-m", "http.server", "8080", "--bind", "0.0.0.0"]

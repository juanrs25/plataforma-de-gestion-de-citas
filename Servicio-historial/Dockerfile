FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# El -u es MAGIA. Obliga a Python a escupir los logs a Docker de inmediato.
CMD ["python", "-u", "app.py"]
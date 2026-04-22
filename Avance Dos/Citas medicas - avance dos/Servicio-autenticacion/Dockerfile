# FROM nginx:latest
# COPY /sitio /usr/share/nginx/html


FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

CMD [ "python", "app.py"]
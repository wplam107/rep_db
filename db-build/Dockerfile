FROM python:3.9-slim-buster

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "update_database.py"]

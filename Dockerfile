FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -U pip
RUN python -m pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python", "main.py" ]
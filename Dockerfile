FROM python:3.8 AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

WORKDIR /app

COPY . .

ENV PYTHONUNBUFFFERED=1

CMD ["sleep", "99999"]

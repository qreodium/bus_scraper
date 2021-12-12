FROM python:3.8-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY . .

ENV PYTHONUNBUFFFERED=1

CMD ["python3", "./bus_checker.py"]

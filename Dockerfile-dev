FROM python:3.9-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt

# COPY ./src/stock_trader.py .

# ENTRYPOINT ["python3", "stock_trader.py"]

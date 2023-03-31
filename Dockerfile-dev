FROM python:3.9-slim

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt

# COPY ./src/stock_trader.py .

# ENTRYPOINT ["python3", "stock_trader.py"]

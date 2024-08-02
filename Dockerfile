FROM python:3.12

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python3", "main.py"]
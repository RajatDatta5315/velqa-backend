FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Isse Back4app ko port dikhega
EXPOSE 5000

# Server run karte waqt environment port use karega
CMD ["python", "server_v2.py"]

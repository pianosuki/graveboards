FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "setup.py"]

CMD ["uvicorn", "main:connexion_app", "--host", "0.0.0.0", "--port", "8000"]
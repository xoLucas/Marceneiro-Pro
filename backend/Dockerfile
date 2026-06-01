FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_USE_SQLITE=1

# Rodar migrations e seed no build
RUN python manage.py migrate
RUN python manage.py seed_dados

EXPOSE 8000
CMD ["gunicorn", "marcenaria.wsgi:application", "--bind", "0.0.0.0:$PORT"]

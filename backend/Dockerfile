FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

EXPOSE 8000
CMD ["/app/startup.sh"]

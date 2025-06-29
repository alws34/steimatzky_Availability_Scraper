FROM python:3.11-slim

# Set up environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

EXPOSE 8091

# Run Flask app
CMD ["python", "app.py"]

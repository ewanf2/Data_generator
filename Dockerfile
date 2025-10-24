FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY App.py functions.py models.py ./

# Create schemas directory and initialize empty schemas file
RUN mkdir -p /app/schemas && \
    echo '{}' > /app/schemas/schemas.json

# Expose application port
EXPOSE 5050
CMD ["waitress-serve", "--listen=0.0.0.0:80", "App:App"]

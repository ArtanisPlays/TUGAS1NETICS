# Use a tiny Python image
FROM python:3.9-alpine

WORKDIR /app

# Copy your Python API script
COPY server.py .

EXPOSE 8080

# Run the API
CMD ["python", "server.py"]
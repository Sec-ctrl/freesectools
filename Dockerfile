# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the Gunicorn app
EXPOSE 8000

# Run Gunicorn to serve the app
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "app:app"]

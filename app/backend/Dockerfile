# Use an official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app/backend

# Add PYTHONPATH
ENV PYTHONPATH=/app

# Copy only the requirements file first
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the rest of the source code
COPY . .

# Expose the port for FastAPI
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

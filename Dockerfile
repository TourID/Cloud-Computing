# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED True

# Set the working directory in the container
WORKDIR /app

# Copy the project files to the working directory
COPY . ./

# Install dependencies
RUN pip install -r requirements.txt

# Expose port 8080
EXPOSE 8080

# Command to run the application (assuming your app listens on port 8080)
CMD ["python", "app.py"]

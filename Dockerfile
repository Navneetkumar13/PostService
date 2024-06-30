# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8001 available to the world outside this container
EXPOSE 8001

# Define environment variable
ENV DJANGO_SETTINGS_MODULE=test_service_1.settings

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
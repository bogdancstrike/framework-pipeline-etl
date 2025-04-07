# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 7001

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Create a non-root user with UID 1000
RUN groupadd -g 1000 mygroup && \
    useradd -u 1000 -g mygroup -s /bin/bash -m myuser

# Create /app directory and set permissions
RUN mkdir -p /app && chown -R myuser:mygroup /app

# Run the application
CMD ["python3", "main.py"]

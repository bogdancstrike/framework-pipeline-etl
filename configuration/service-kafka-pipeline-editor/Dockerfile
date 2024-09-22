# Use the official Python image as a base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Update pip to the latest version
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]

# docker build --no-cache -t service-kafka-pipeline-editor:latest .
# docker tag service-kafka-pipeline-editor:latest localhost:32000/service-kafka-pipeline-editor:latest
# docker push localhost:32000/service-kafka-pipeline-editor:latest
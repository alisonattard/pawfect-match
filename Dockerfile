# Use an official Python runtime as a base image
FROM python:3.9-slim

EXPOSE 5000

# Set environment variables to prevent Python from writing .pyc files and buffering stdout
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install necessary system dependencies (git, etc.)
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean

# Clone the CLIP repository and install dependencies
RUN git clone https://github.com/openai/CLIP.git /app/CLIP
WORKDIR /app/CLIP
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .
RUN pip install transformers
RUN pip install scikit-learn
RUN pip install sentencepiece
RUN pip install protobuf
RUN pip install numpy
RUN pip install requests
RUN pip install sacremoses
RUN pip install firebase_admin

# Install Flask and other dependencies for image processing
RUN pip install Flask Pillow torch

COPY static /app/static

COPY templates /app/templates

# Copy the local model directory into the container
COPY flan_t5_trained_model /app/flan_t5_model

# Copy the server script (ai_server.py) into the container
COPY app.py /app/

# Copy the Firebase key into the container
COPY firebase-key.json /app/firebase-key.json

# Expose Flask port
EXPOSE 6000

# Set the working directory
WORKDIR /app

# Set the command to run your Flask app
CMD ["python", "app.py"]

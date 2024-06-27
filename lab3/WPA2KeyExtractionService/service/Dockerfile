# Use the official CUDA base image
FROM nvidia/cuda:11.8.0-base-ubuntu22.04

# Set non-interactive frontend for apt-get
ARG DEBIAN_FRONTEND=noninteractive

# Set timezone to avoid interactive prompt
ENV TZ=Etc/UTC

# Install dependencies and Python 3.9
RUN apt-get update && apt-get install -y \
    tzdata \
    software-properties-common \
    && ln -fs /usr/share/zoneinfo/$TZ /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.9 \
    python3.9-venv \
    python3.9-dev \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install pip
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Add wait-for-it script
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/src/app/wait-for-it.sh
RUN chmod +x /usr/src/app/wait-for-it.sh

# Run the application
CMD ["./wait-for-it.sh", "rabbitmq:5672", "--", "python3.9", "./processor.py"]

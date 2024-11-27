# Use the official OpenJDK 11 image as a base image
FROM openjdk:11-jdk-slim as builder

# Install Oracle Instant Client, gzip, and other dependencies
RUN apt-get update && apt-get install -y \
        curl \
        tar \
        python3 \
        python3-pip \
        python3-setuptools \
        python3-libs \
        python3-cx_Oracle \
        gzip && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /workspace

# Download Liquibase and extract it
RUN curl -LJO https://github.com/liquibase/liquibase/releases/download/v4.27.0/liquibase-4.27.0.tar.gz && \
    mkdir -p /liquibase && \
    tar -xzf liquibase-4.27.0.tar.gz -C /liquibase && \
    rm liquibase-4.27.0.tar.gz

# Set environment variables for Liquibase
ENV LIQUIBASE_HOME=/liquibase
ENV PATH=$LIQUIBASE_HOME:$PATH
ENV TNS_ADMIN=/workspace/Wallet_2

# Copy necessary files for Liquibase (adjust paths as needed)
COPY ./lq/changelog /liquibase/changelog
COPY ./Wallet_2 /workspace/Wallet_2
COPY ./jars /workspace/jars

# Validate Liquibase installation
RUN liquibase --version

# Run Liquibase update commands
RUN liquibase \
    --changeLogFile=/liquibase/changelog/master-changelog.xml \
    --url=jdbc:oracle:thin:@testcloneautomatecicdqa_tp?TNS_ADMIN=/workspace/Wallet_2 \
    --username=todouser \
    --password=Igdefault123 \
    --search-path=/ \
    --classpath=/workspace/jars/ojdbc8.jar \
    update

# Switch to application build stage
WORKDIR /app

# Copy requirements and install dependencies for the Flask application
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application
COPY . .

# Expose Flask application port
EXPOSE 5000

# Set the command to run the Flask application
CMD ["python3", "app3.py"]

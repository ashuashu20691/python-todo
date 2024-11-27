# Base image based on oraclelinux:7-slim
FROM oraclelinux:7-slim as builder

# Install Oracle Instant Client and other dependencies
RUN yum -y install oraclelinux-developer-release-el7 oracle-instantclient-release-el7 && \
    yum -y install python3 \
                   python3-libs \
                   python3-pip \
                   python3-setuptools \
                   python36-cx_Oracle && \
    yum -y install tar curl && \
    rm -rf /var/cache/yum/*

# Set the working directory inside the container
WORKDIR /workspace

# Download Liquibase and the required JDBC driver
RUN curl -LJO https://github.com/liquibase/liquibase/releases/download/v4.27.0/liquibase-4.27.0.tar.gz && \
    tar -xzf liquibase-4.27.0.tar.gz

# Copy Liquibase configuration files
COPY ./lq /workspace/lq
COPY ./Wallet_2 /workspace/Wallet_2
COPY ./jars /workspace/jars

# Set environment variables for Liquibase
ENV LIQUIBASE_HOME=/workspace/liquibase
ENV PATH=$LIQUIBASE_HOME:$PATH
ENV TNS_ADMIN=/workspace/Wallet_2

# Run Liquibase update commands
RUN ./liquibase/liquibase \
    --changeLogFile=/workspace/lq/master-changelog.xml \
    --url=jdbc:oracle:thin:@testcloneautomatecicdqa_tp?TNS_ADMIN=/app/Wallet_2 \
    --username=todouser \
    --password=Igdefault123 \
    --classpath=/workspace/jars/ojdbc8.jar \
    update

# Build Flask application
WORKDIR /app
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY . .

# Expose Flask port
EXPOSE 5000

# Command to run the Flask application
CMD ["python3", "app3.py"]

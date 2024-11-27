# Base image based on Oracle Linux 7-slim
FROM oraclelinux:7-slim as builder

# Install Oracle Instant Client, gzip, and other dependencies
RUN yum -y install oraclelinux-developer-release-el7 oracle-instantclient-release-el7 && \
    yum -y install python3 \
                   python3-libs \
                   python3-pip \
                   python3-setuptools \
                   python36-cx_Oracle \
                   tar \
                   curl \
                   gzip && \
    rm -rf /var/cache/yum/*


# Download and install OpenJDK 11 from AdoptOpenJDK (or another distribution)
RUN curl -L -o /tmp/openjdk-11-linux-x64.tar.gz https://github.com/AdoptOpenJDK/openjdk11-binaries/releases/download/jdk-11.0.10+9/OpenJDK11U-jdk_x64_linux_hotspot_11.0.10_9.tar.gz && \
    mkdir -p /usr/lib/jvm && \
    tar -xzf /tmp/openjdk-11-linux-x64.tar.gz -C /usr/lib/jvm && \
    rm /tmp/openjdk-11-linux-x64.tar.gz

# Set JAVA_HOME for Java 11
ENV JAVA_HOME=/usr/lib/jvm/jdk-11.0.10+9
ENV PATH=$JAVA_HOME/bin:$PATH

# Verify Java installation
RUN java -version

# Set the working directory inside the container
WORKDIR /workspace

RUN curl -LJO https://github.com/liquibase/liquibase/releases/download/v4.27.0/liquibase-4.27.0.tar.gz && \
    mkdir -p /liquibase && \
    tar -xzf liquibase-4.27.0.tar.gz -C /liquibase && \
    rm liquibase-4.27.0.tar.gz

# Set environment variables for Liquibase
ENV LIQUIBASE_HOME=/liquibase
ENV PATH=$LIQUIBASE_HOME:$PATH
ENV TNS_ADMIN=/workspace/Wallet_2

# Copy necessary files for Liquibase
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

# Copy requirements and install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application
COPY . .

# Expose Flask application port
EXPOSE 5000

# Set the command to run the Flask application
CMD ["python3", "app3.py"]

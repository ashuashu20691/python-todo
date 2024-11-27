# build the image based on oraclelinux:7-slim
FROM oraclelinux:7-slim

# Install Oracle Instant Client and Python dependencies
RUN yum -y install oraclelinux-developer-release-el7 oracle-instantclient-release-el7 && \
    yum -y install python3 \
                   python3-libs \
                   python3-pip \
                   python3-setuptools \
                   python36-cx_Oracle && \
    rm -rf /var/cache/yum/*

# Metadata about the maintainer
LABEL Maintainer_Name="Vijay balebail" Maintainer_Email="vijay.balebail@oracle.com"

# Set the working directory inside the container
WORKDIR /

# Set environment variables
ENV FLASK_APP app.py
ENV FLASK_ENV development
# Set environment variables
ENV TNS_ADMIN=/app/Wallet_2

# Copy the requirements file and install dependencies
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

# Create app directory and copy project files
RUN mkdir /app
WORKDIR /app
COPY . .

# Copy Oracle Wallet files to the container
COPY Wallet_2 /app/Wallet_2

# Expose the Flask port
EXPOSE 5000

# Command to run the Flask application
CMD ["python3", "app3.py"]


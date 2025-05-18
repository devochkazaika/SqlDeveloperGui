
FROM debian:bookworm-slim

ARG uid=0

RUN test -n "${uid}" || (echo "docker build-arg uid must be set" && false)

RUN apt-get update && \
    apt-get install -y \
    openjdk-17-jdk \
    wget \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2 \
    rpm2cpio \
    cpio \
    && rm -rf /var/lib/apt/lists/*
    
RUN wget --no-check-certificate --quiet \
    "https://download.oracle.com/otn_software/java/sqldeveloper/sqldeveloper-24.3.1-347.1826.noarch.rpm" -O /tmp/sqldeveloper.rpm

RUN rpm2cpio /tmp/sqldeveloper.rpm | cpio -idmv && \
    rm /tmp/sqldeveloper.rpm

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

RUN ln -s /opt/instantclient/sqlplus /usr/bin/sqlplus64

ENTRYPOINT ["/opt/sqldeveloper/sqldeveloper.sh"]
        
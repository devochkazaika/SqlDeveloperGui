FROM debian:bookworm-slim

ARG uid

RUN test -n "${uid}" || (echo "docker build-arg uid must be set" && false)

# Устанавливаем зависимости, включая JDK и GUI-библиотеки
RUN apt-get update && \
    apt-get install -y \
    openjdk-17-jdk \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Копируем SQL Developer
COPY sqldeveloper /usr/sqldeveloper

# Создаем пользователя
RUN useradd --create-home --shell /bin/bash -u ${uid} --user-group debian && \
    chown -R debian:debian /usr/sqldeveloper 

USER debian

# Правильный путь для JDK 17
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

CMD ["/usr/sqldeveloper/opt/sqldeveloper/sqldeveloper.sh"]

#!/bin/bash

# Подключение к базе данных Oracle
# Устанавливаем переменные окружения для подключения
export ORACLE_SID=XE
export ORACLE_HOME=/opt/oracle/product/18c/dbhome_1
export PATH=$PATH:$ORACLE_HOME/bin

# Параметры подключения
DB_HOST="192.168.43.104"
DB_PORT="1521"
DB_USER="SYSTEM"
DB_PASS="password"

EXIT;
EOF

if [ $? -eq 0 ]; then
    echo "Connection to Oracle DB was successful!"
else
    echo "Failed to connect to Oracle DB."
    exit 1
fi

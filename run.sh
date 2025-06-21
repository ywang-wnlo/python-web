#!/bin/sh

# 该脚本仅用于 Docker 环境

if [ ! -f /app/.init_db ]; then
    echo "第一次启动，初始化数据库"
    flask --app flaskr init-db
    if [ $? -ne 0 ]; then
        echo "初始化数据库失败"
        exit 1
    fi
    touch /app/.init_db
    SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
    echo "SECRET_KEY = '$SECRET_KEY'" | tee /app/instance/config.py
fi

waitress-serve --call 'flaskr:create_app'

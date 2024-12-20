# 基础镜像
FROM alpine:latest

# 设置工作目录
WORKDIR /app

# 复制当前目录下的文件到工作目录
COPY . /app

# 安装 python3, pip3, curl, flask 和 waitress
# 附加执行权限
RUN apk add --no-cache python3 py3-pip py3-flask py3-waitress curl && \
    chmod +x run.sh

# 暴露端口
EXPOSE 8080

# 启动服务
CMD ["./run.sh"]

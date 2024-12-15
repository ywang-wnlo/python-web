# 基础镜像
FROM alpine:latest

# 安装 python3, pip3, curl
RUN apk add --no-cache python3 py3-pip curl

# 安装 flask 和 waitress
RUN apk add py3-flask py3-waitress

# 设置工作目录
WORKDIR /app

# 复制当前目录下的文件到工作目录
COPY . /app

# 删除不需要的文件
RUN rm -rf .git .venv instance

# 附加执行权限
RUN chmod +x run.sh

# 暴露端口
EXPOSE 8080

# 启动服务
CMD ["./run.sh"]

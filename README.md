# NavBoard

NavBoard 是一个简洁高效的内外网服务导航管理平台。支持用户登录后添加、管理各类服务入口，包括域名访问、外网直连和内网直连等多种方式，适合个人或团队集中管理常用服务和资源。

## 功能特性

- 添加、编辑、删除导航条目
- 支持外网域名、外网 IP、内网 IP 及端口的多种访问方式
- 简洁美观的 Web 界面，基于 Bulma 框架

## 快速开始

1. 克隆项目并安装依赖
2. 初始化数据库
3. 启动服务

    ```bash
    git clone <your-repo-url>
    cd NavBoard
    pip install flask
    flask --app flaskr init-db
    flask --app flaskr run --debug
    ```

访问 [http://localhost:5000](http://localhost:5000) 使用 NavBoard

## 生产环境（Docker）

构建镜像：

```bash
docker build -t navboard .
```

初始化数据库：

```bash
docker run -p [port]:8080 -it --restart unless-stopped --name navboard navboard
```

初始化后可用 ctrl+c 停止容器。

正常运行容器：

```bash
docker start navboard
```

import os

from flask import Flask


def create_app():
    """创建并配置 Flask 应用实例"""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # 默认密钥，建议在生产环境中通过实例配置覆盖
        SECRET_KEY="dev",
        # 数据库存储在 instance 文件夹
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    # 如果存在实例配置文件（config.py），则加载
    app.config.from_pyfile("config.py", silent=True)

    # 确保 instance 文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 注册数据库相关命令
    from . import db
    db.init_app(app)

    # 注册蓝图（用户认证、导航管理）
    from . import auth
    from . import navboard
    from . import webtools

    app.register_blueprint(auth.bp)
    app.register_blueprint(navboard.bp)
    app.register_blueprint(webtools.bp)

    # 让 url_for('index') 等价于 url_for('navboard.index')
    # 本项目直接将 navboard 作为主页面
    app.add_url_rule("/", endpoint="index")

    return app

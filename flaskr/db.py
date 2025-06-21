import sqlite3

import click
from flask import current_app
from flask import g
from werkzeug.security import generate_password_hash
from getpass import getpass


def get_db():
    """连接应用配置的数据库。每个请求唯一，重复调用会复用同一连接"""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    """如果本次请求连接了数据库，则关闭该连接"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """清空现有数据并创建新表结构"""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def create_user(user, pwd):
    """创建初始用户"""
    db = get_db()
    db.execute(
        "INSERT INTO user (username, password) VALUES (?, ?)",
        (user, generate_password_hash(pwd, method="pbkdf2")),
    )
    db.commit()
    click.echo("[%s]创建成功，密码[%s]." % (user, pwd))


@click.command("init-db")
def init_db_command():
    """清空现有数据并创建新表结构，然后创建初始账户"""
    init_db()
    click.echo("数据库初始化完成，开始创建账户")
    _user = input("用户名: ")
    _pwd = getpass("密码: ")
    create_user(_user, _pwd)


def init_app(app):
    """将数据库相关函数注册到 Flask 应用"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

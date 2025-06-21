import functools
import time

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def login_required(view):
    """视图装饰器：未登录用户会被重定向到登录页面。"""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """如果 session 中存在用户 id，则从数据库加载用户信息到 g.user。"""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/login", methods=("GET", "POST"))
def login():
    """登录已注册用户，将用户 id 存入 session。"""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "错误的用户名或密码"
        elif not check_password_hash(user["password"], password):
            error = "错误的用户名或密码"

        if error is None:
            # 登录成功，清空 session 并存储用户 id，跳转到首页
            session.clear()
            session["user_id"] = user["id"]
            print("%s - %s login success with user[%s]" % (
                now(), request.remote_addr, username))
            return redirect(url_for("index"))

        flash(error)
        print("%s - %s try to login failed, with user[%s] password[%s]" % (
            now(), request.remote_addr, username, password))

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """注销当前用户，清除 session 并返回首页。"""
    session.clear()
    print("%s - %s logout with user[%s]" %
          (now(), request.remote_addr, g.user["username"]))
    return redirect(url_for("index"))

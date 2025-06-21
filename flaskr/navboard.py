import os
import time

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

bp = Blueprint("navboard", __name__)


def set_value_to_gmap(k, v):
    # 将键值对写入 gmap（sqlite）表，用于缓存全局信息
    db = get_db()
    db.execute(
        "REPLACE INTO gmap (k, v) VALUES (?, ?)",
        (k, v),
    )
    db.commit()


def get_value_from_gmap(k) -> str:
    # 从 gmap（sqlite）表获取指定键的值
    db = get_db()
    ret = db.execute(
        "SELECT v FROM gmap WHERE k = ?",
        (k,)
    ).fetchone()
    return ret["v"] if ret else None


def get_wan_ip() -> str:
    # 获取外网 IP，优先用缓存，过期则重新获取
    wan_ip = get_value_from_gmap("wan_ip")
    last = get_value_from_gmap("last")
    if last:
        last = float(last)
    now = time.time()
    # 缓存 60 秒内直接返回
    if wan_ip and last and (now - last < 60):
        return wan_ip

    wan_ip = os.popen("curl -s 4.ipw.cn").read().strip()
    if wan_ip:
        # 更新缓存
        set_value_to_gmap("wan_ip", wan_ip)
        set_value_to_gmap("last", now)
        return wan_ip
    else:
        return None


@bp.route("/")
@login_required
def index():
    """展示所有导航条目（nav_entry），按 url 排序"""
    db = get_db()
    nav_entrys = db.execute(
        "SELECT id, title, url, port, local_ip, author_id"
        " FROM nav_entry ORDER BY url ASC"
    ).fetchall()
    g.wan_ip = get_wan_ip()
    return render_template("navboard/index.html", nav_entrys=nav_entrys)


def get_nav_entry(id, check_author=True):
    """根据 id 获取导航条目及其作者

    检查条目是否存在，并可选校验当前用户是否为作者
    :param id: 要获取的 nav_entry 的 id
    :param check_author: 是否校验作者
    :return: 带作者信息的 nav_entry
    :raise 404: 条目不存在
    :raise 403: 当前用户不是作者
    """
    nav_entry = (
        get_db()
        .execute(
            "SELECT id, title, url, port, local_ip, author_id"
            " FROM nav_entry WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if nav_entry is None:
        abort(404, f"导航条目 id {id} 不存在。")

    if check_author and nav_entry["author_id"] != g.user["id"]:
        abort(403)

    return nav_entry


def valid_url(url) -> bool:
    """校验链接格式是否为 http(s):// 开头"""
    return url.startswith("http://") or url.startswith("https://")


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """为当前用户创建新的导航条目"""
    if request.method == "POST":
        title = request.form["title"]
        protocol = request.form["protocol"]
        url = request.form["url"]
        port = request.form["port"]
        local_ip = request.form["local_ip"]
        error = None

        if not url:
            error = "必须输入链接"
        elif not title:
            error = "必须输入标题"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO nav_entry (title, url, port, local_ip, author_id) VALUES (?, ?, ?, ?, ?)",
                (title, protocol + url, port, local_ip, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("navboard.index"))

    return render_template("navboard/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """仅允许作者本人修改导航条目"""
    nav_entry = get_nav_entry(id)

    if request.method == "POST":
        title = request.form["title"]
        url = request.form["url"]
        port = request.form["port"]
        local_ip = request.form["local_ip"]
        error = None

        if not url:
            error = "必须输入链接"
        elif not valid_url(url):
            error = "链接格式不正确，必须包含 http(s)://"
        elif not title:
            error = "必须输入标题"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE nav_entry SET title = ?, url = ? , port = ?, local_ip = ? WHERE id = ?",
                (title, url, port, local_ip, id)
            )
            db.commit()
            return redirect(url_for("navboard.index"))

    return render_template("navboard/update.html", nav_entry=nav_entry)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """删除导航条目，确保条目存在且当前用户为作者"""
    get_nav_entry(id)
    db = get_db()
    db.execute("DELETE FROM nav_entry WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("navboard.index"))

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

bp = Blueprint("blog", __name__)


def set_value_to_gmap(k, v):
    # set value to sqlite
    db = get_db()
    db.execute(
        "REPLACE INTO gmap (k, v) VALUES (?, ?)",
        (k, v),
    )
    db.commit()

def get_value_from_gmap(k) -> str:
    # get value from sqlite
    db = get_db()
    ret = db.execute(
        "SELECT v FROM gmap WHERE k = ?",
        (k,)
    ).fetchone()
    return ret["v"] if ret else None

def get_ip() -> str:
    # try get ip from sqlite
    ip = get_value_from_gmap("ip")
    last = float(get_value_from_gmap("last"))
    now = time.time()
    # use the cached ip if it's not expired
    if ip and last and (now - last < 60):
        return ip

    ret = os.popen("curl ifconfig.me/ip").read()
    if ret:
        # update the record in sqlite
        set_value_to_gmap("ip", ret)
        set_value_to_gmap("last", now)
        return ret
    else:
        return None

@bp.route("/")
@login_required
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT id, title, url, port, author_id"
        " FROM post ORDER BY url ASC"
    ).fetchall()
    g.ip = get_ip()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT id, title, url, port, author_id"
            " FROM post WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post

def valid_url(url) -> bool:
    """Check if the url is valid."""
    return url.startswith("http://") or url.startswith("https://")

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        url = request.form["url"]
        port = request.form["port"]
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
                "INSERT INTO post (title, url, port, author_id) VALUES (?, ?, ?, ?)",
                (title, url, port, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        url = request.form["url"]
        port = request.form["port"]
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
                "UPDATE post SET title = ?, url = ? , port = ? WHERE id = ?",
                (title, url, port, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))

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

def get_wan_ip() -> str:
    # try get ip from sqlite
    wan_ip = get_value_from_gmap("wan_ip")
    last = get_value_from_gmap("last")
    if last:
        last = float(last)
    now = time.time()
    # use the cached ip if it's not expired
    if wan_ip and last and (now - last < 60):
        return wan_ip

    wan_ip = os.popen("curl -s 4.ipw.cn").read().strip()
    if wan_ip:
        # update the record in sqlite
        set_value_to_gmap("wan_ip", wan_ip)
        set_value_to_gmap("last", now)
        return wan_ip
    else:
        return None

@bp.route("/")
@login_required
def index():
    """Show all the nav_entrys, most recent first."""
    db = get_db()
    nav_entrys = db.execute(
        "SELECT id, title, url, port, local_ip, author_id"
        " FROM nav_entry ORDER BY url ASC"
    ).fetchall()
    g.wan_ip = get_wan_ip()
    return render_template("navboard/index.html", nav_entrys=nav_entrys)


def get_nav_entry(id, check_author=True):
    """Get a nav_entry and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of nav_entry to get
    :param check_author: require the current user to be the author
    :return: the nav_entry with author information
    :raise 404: if a nav_entry with the given id doesn't exist
    :raise 403: if the current user isn't the author
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
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and nav_entry["author_id"] != g.user["id"]:
        abort(403)

    return nav_entry

def valid_url(url) -> bool:
    """Check if the url is valid."""
    return url.startswith("http://") or url.startswith("https://")

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new nav_entry for the current user."""
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
    """Update a nav_entry if the current user is the author."""
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
    """Delete a nav_entry.

    Ensures that the nav_entry exists and that the logged in user is the
    author of the nav_entry.
    """
    get_nav_entry(id)
    db = get_db()
    db.execute("DELETE FROM nav_entry WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("navboard.index"))

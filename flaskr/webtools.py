from flask import Blueprint, render_template, request
from urllib.parse import unquote

bp = Blueprint("webtools", __name__, template_folder="webtools")

def decode_real_url(url):
    """解码 URL，去除可能的编码字符"""
    prev = url
    curr = unquote(prev)
    while curr != prev:
        prev = curr
        curr = unquote(prev)
    # 如果有多个 http(s) 前缀，保留最后一个
    http_prefixes = ["http://", "https://"]
    for prefix in http_prefixes:
        if prefix in curr:
            curr = prefix + curr.split(prefix)[-1] 
    return curr

def make_iina_output(value):
    """处理输入的 URL，返回解码后的结果或错误提示"""
    if value.startswith("http://") or value.startswith("https://"):
        return decode_real_url(value)
    return "不是有效的 URL"

@bp.route("/quick-iina", methods=("GET", "POST"))
def quick_iina():
    """无需登录即可访问的 quick-iina 页面，提供一个输入框和按钮。"""
    result = None
    if request.method == "POST":
        value = request.form.get("iina_input")
        result = make_iina_output(value)
    return render_template("webtools/quick-iina.html", iina_output=result)

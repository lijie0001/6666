# -*- coding: utf-8 -*-
"""
Flask 网页 - 展示爬虫抓取的内容
Railway 会注入 PORT 环境变量
"""
import os
from pathlib import Path
from flask import Flask, render_template
from crawler import crawl
from image_crawler import crawl_and_save, load_from_json

app = Flask(__name__)


@app.route("/health")
def health():
    """健康检查，Railway 用此判断服务是否就绪"""
    return "ok", 200


@app.route("/")
def index():
    try:
        items = crawl()
    except Exception:
        items = [{"title": "加载中...", "link": "#", "meta": ""}]
    return render_template("index.html", items=items)


@app.route("/images")
def images():
    """图片页：爬取并展示，地址已存到 data/images.json"""
    try:
        items = crawl_and_save()
    except Exception:
        items = []
    return render_template("images.html", items=items)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    is_prod = "RAILWAY_ENVIRONMENT" in os.environ
    if is_prod:
        app.run(host="0.0.0.0", port=port)
    else:
        root = Path(__file__).parent
        extra_files = list(root.glob("templates/**/*")) + [root / "crawler.py", root / "image_crawler.py"]
        extra_files = [str(p) for p in extra_files if p.exists()]
        app.run(host="0.0.0.0", port=port, debug=True, extra_files=extra_files)

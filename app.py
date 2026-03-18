# -*- coding: utf-8 -*-
"""
Flask 网页 - 展示爬虫抓取的内容
Railway 会注入 PORT 环境变量
"""
import os
import threading
import time
from pathlib import Path
from flask import Flask, render_template
from crawler import crawl
from image_crawler import crawl_and_save, load_from_json

app = Flask(__name__)

# 图片缓存，后台定时更新
_images_cache: list = []
_images_lock = threading.Lock()

# 爬取间隔（秒），默认 5 分钟
CRAWL_INTERVAL = int(os.environ.get("CRAWL_INTERVAL", 300))


def _update_images():
    """后台任务：爬取图片并更新缓存"""
    global _images_cache
    while True:
        time.sleep(CRAWL_INTERVAL)  # 先等待，避免与启动时重复
        try:
            items = crawl_and_save()
            with _images_lock:
                _images_cache = items
            print(f"[{time.strftime('%H:%M:%S')}] 图片已更新，共 {len(items)} 张")
        except Exception as e:
            print(f"爬取失败: {e}")


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
    """图片页：展示缓存内容，后台每 N 分钟自动更新"""
    with _images_lock:
        items = _images_cache.copy()
    if not items:
        items = load_from_json()
    return render_template("images.html", items=items)


if __name__ == "__main__":
    # 启动时先爬一次
    try:
        _images_cache.extend(crawl_and_save())
    except Exception:
        pass
    # 后台线程：每 CRAWL_INTERVAL 秒爬一次
    t = threading.Thread(target=_update_images, daemon=True)
    t.start()
    print(f"图片爬虫已启动，每 {CRAWL_INTERVAL} 秒更新一次")

    port = int(os.environ.get("PORT", 5000))
    print(f"Starting on 0.0.0.0:{port}")
    is_prod = "RAILWAY_ENVIRONMENT" in os.environ
    if is_prod:
        app.run(host="0.0.0.0", port=port)
    else:
        root = Path(__file__).parent
        extra_files = list(root.glob("templates/**/*")) + [root / "crawler.py", root / "image_crawler.py"]
        extra_files = [str(p) for p in extra_files if p.exists()]
        app.run(host="0.0.0.0", port=port, debug=True, extra_files=extra_files)

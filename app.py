# -*- coding: utf-8 -*-
"""
Flask 网页 - 展示爬虫抓取的内容
Railway 会注入 PORT 环境变量
"""
import os
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request
from crawler import crawl
from image_crawler import crawl_and_save, load_from_json, list_sources

app = Flask(__name__)

# 爬取间隔（秒），默认 60 秒
CRAWL_INTERVAL = int(os.environ.get("CRAWL_INTERVAL", 60))


def _update_images():
    """后台任务：按分类爬取并分别存 JSON"""
    while True:
        time.sleep(CRAWL_INTERVAL)  # 先等待，避免与启动时重复
        try:
            items = crawl_and_save()
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


PER_PAGE = 9


@app.route("/images")
def images():
    """图片页：数据源=分类，选人像看人像.json，选漫威看漫威.json"""
    source = request.args.get("source", "")
    page = request.args.get("page", 1, type=int)
    page = max(1, page)

    sources = list_sources()
    if not source and sources:
        source = sources[0]["name"]
    items = load_from_json(source_name=source) if source else []
    total = len(items)
    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = min(page, total_pages)
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    page_items = items[start:end]

    return render_template(
        "images.html",
        items=page_items,
        current_page=page,
        total_pages=total_pages,
        total=total,
        crawl_interval=CRAWL_INTERVAL,
        sources=sources,
        current_source=source or "",
    )


if __name__ == "__main__":
    # 启动时先爬一次
    try:
        crawl_and_save()
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

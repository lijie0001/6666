# -*- coding: utf-8 -*-
"""
图片爬虫 - 抓取图片地址并保存到 JSON
使用 picsum.photos（免费占位图，专为开发设计）
"""
import json
import os
import random
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
IMAGES_JSON = DATA_DIR / "images.json"

# picsum.photos 提供免费图片 API，无反爬
PICSUM_API_BASE = "https://picsum.photos/v2/list"


def crawl_images_from_api() -> list[dict]:
    """从 Picsum API 获取图片列表（每次随机页码，保证更新后有新图）"""
    try:
        page = random.randint(1, 50)  # 随机页，每次爬取不同图片
        url = f"{PICSUM_API_BASE}?page={page}&limit=30"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        items = []
        for item in data:
            items.append({
                "url": item.get("download_url", ""),
                "author": item.get("author", ""),
                "id": item.get("id", ""),
                "width": item.get("width", 0),
                "height": item.get("height", 0),
            })
        return items
    except Exception as e:
        return [{"url": "", "author": str(e), "id": "", "width": 0, "height": 0}]


def crawl_images_from_html(url: str = None) -> list[dict]:
    """从网页中提取 img 标签的图片地址"""
    url = url or os.getenv("IMAGE_CRAWL_URL", "https://picsum.photos/")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        seen = set()
        for img in soup.find_all("img", src=True):
            src = img.get("src", "")
            if not src or src in seen:
                continue
            seen.add(src)
            full_url = urljoin(url, src)
            alt = img.get("alt", "") or "图片"
            items.append({"url": full_url, "author": alt, "id": str(len(items)), "width": 0, "height": 0})
            if len(items) >= 30:
                break
        return items
    except Exception as e:
        return [{"url": "", "author": str(e), "id": "", "width": 0, "height": 0}]


def save_to_json(items: list[dict], path: Path = IMAGES_JSON) -> Path:
    """保存到 JSON 文件"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # Railway 等环境可能无法写入，不阻塞
    return path


def load_from_json(path: Path = IMAGES_JSON) -> list[dict]:
    """从 JSON 加载"""
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def crawl_and_save(use_api: bool = True) -> list[dict]:
    """爬取图片并保存到 JSON，返回列表"""
    items = crawl_images_from_api() if use_api else crawl_images_from_html()
    save_to_json(items)
    return items

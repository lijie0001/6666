# -*- coding: utf-8 -*-
"""
图片爬虫 - 抓取图片地址并保存到 JSON
使用 picsum.photos（免费占位图，专为开发设计）
每文件最多 20 万条，满则新建文件；支持分类（按爬取来源网站）
"""
import json
import os
import random
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"
MAX_PER_FILE = 200000  # 每文件 20 万条

# picsum.photos 提供免费图片 API，无反爬
PICSUM_API_BASE = "https://picsum.photos/v2/list"


def _domain_from_url(url: str) -> str:
    """从 URL 提取域名作为分类"""
    try:
        return urlparse(url).netloc or "未分类"
    except Exception:
        return "未分类"


def crawl_images_from_api() -> list[dict]:
    """从 Picsum API 获取图片列表（分类=来源网站）"""
    source = "picsum.photos"
    try:
        page = random.randint(1, 50)
        url = f"{PICSUM_API_BASE}?page={page}&limit=30"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        items = []
        for item in data:
            items.append({
                "id": str(item.get("id", "")),
                "url": item.get("download_url", ""),
                "category": source,
            })
        return items
    except Exception:
        return [{"id": "", "url": "", "category": source}]


def crawl_images_from_html(url: str = None) -> list[dict]:
    """从网页中提取 img 标签的图片地址（分类=爬取网站域名）"""
    crawl_url = url or os.getenv("IMAGE_CRAWL_URL", "https://picsum.photos/")
    source = _domain_from_url(crawl_url)
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(crawl_url, headers=headers, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        seen = set()
        for img in soup.find_all("img", src=True):
            src = img.get("src", "")
            if not src or src in seen:
                continue
            seen.add(src)
            full_url = urljoin(crawl_url, src)
            items.append({"id": str(len(items)), "url": full_url, "category": source})
            if len(items) >= 30:
                break
        return items
    except Exception:
        return [{"id": "", "url": "", "category": source}]


def _normalize_item(item: dict) -> dict:
    """保留 id、url、category"""
    return {
        "id": str(item.get("id", "")),
        "url": str(item.get("url", "")),
        "category": str(item.get("category", "") or "未分类"),
    }


def _get_data_files() -> list[Path]:
    """获取所有数据文件，按顺序：images.json, images_2, images_3..."""
    DATA_DIR.mkdir(exist_ok=True)
    files = []
    if (DATA_DIR / "images.json").exists():
        files.append(DATA_DIR / "images.json")
    # images_N.json 按数字排序
    extra = list(DATA_DIR.glob("images_*.json"))
    def _num(p):
        try:
            return int(p.stem.split("_")[-1])
        except (ValueError, IndexError):
            return 0
    for p in sorted(extra, key=_num):
        files.append(p)
    return files


def list_sources() -> list[dict]:
    """列出所有数据源：{name, path, count}"""
    result = []
    for path in _get_data_files():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data) if isinstance(data, list) else 0
        except Exception:
            count = 0
        name = path.stem  # images 或 images_2
        result.append({"name": name, "path": str(path), "count": count})
    return result


def _get_current_write_path() -> Path:
    """获取当前写入目标文件（未满的最后一个，或新建）"""
    files = _get_data_files()
    for path in reversed(files):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if len(data) < MAX_PER_FILE:
                return path
        except Exception:
            continue
    # 全部满或为空，新建
    if not files:
        return DATA_DIR / "images.json"
    last = files[-1]
    stem = last.stem
    if stem == "images":
        return DATA_DIR / "images_2.json"
    num = int(stem.split("_")[-1]) + 1
    return DATA_DIR / f"images_{num}.json"


def save_to_json(items: list[dict], path: Path) -> Path:
    """保存到指定 JSON 文件"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        normalized = [_normalize_item(x) for x in items]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(normalized, f, ensure_ascii=False, separators=(",", ":"))
    except Exception:
        pass
    return path


def load_from_json(path: Path = None, source_name: str = None) -> list[dict]:
    """从 JSON 加载。可传 path 或 source_name（如 images、images_2）"""
    if path is None:
        if source_name:
            p = DATA_DIR / f"{source_name}.json"
        else:
            p = _get_current_write_path()
    else:
        p = Path(path) if isinstance(path, str) else path
    if not p.exists():
        return []
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 兼容旧格式（无 category）
    result = []
    for item in (data if isinstance(data, list) else []):
        d = _normalize_item(item)
        result.append(d)
    return result


def get_categories(source_name: str = None) -> list[str]:
    """获取某数据源下的所有分类（去重）"""
    items = load_from_json(source_name=source_name)
    cats = sorted({x.get("category", "未分类") or "未分类" for x in items if x.get("url")})
    return cats


def crawl_and_save(use_api: bool = True, accumulate: bool = None) -> list[dict]:
    """爬取并保存。满 20 万条则新建文件。"""
    if accumulate is None:
        accumulate = os.environ.get("ACCUMULATE_IMAGES", "true").lower() == "true"
    new_items = crawl_images_from_api() if use_api else crawl_images_from_html()
    if not accumulate:
        path = _get_current_write_path()
        save_to_json(new_items, path)
        return new_items

    path = _get_current_write_path()
    existing = load_from_json(path=path)
    seen_ids = {str(x.get("id", "")) for x in existing}
    merged = existing.copy()
    for item in new_items:
        iid = str(item.get("id", ""))
        url = item.get("url", "")
        if iid and url and iid not in seen_ids:
            merged.append(_normalize_item(item))
            seen_ids.add(iid)

    if len(merged) <= MAX_PER_FILE:
        save_to_json(merged, path)
        return merged
    # 满 20 万：保存当前，新建文件存溢出
    to_save = merged[:MAX_PER_FILE]
    overflow = merged[MAX_PER_FILE:]
    save_to_json(to_save, path)
    next_path = _get_current_write_path()  # 会返回新路径
    save_to_json(overflow, next_path)
    return load_from_json(path=next_path)

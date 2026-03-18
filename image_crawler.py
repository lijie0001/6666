# -*- coding: utf-8 -*-
"""
图片爬虫 - 抓取图片地址并保存到 JSON
多源：picsum、人像、枪械模型、漫威等；每文件最多 20 万条

指定网站抓图（二选一）：
  - data/crawl_urls.txt：每行 网址|分类
  - 环境变量 CRAWL_URLS：url1|分类1,url2|分类2
CRAWL_CATEGORIES: 覆盖内置分类，格式 分类1,分类2
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
# picz.dev 人像/肖像图片，每次请求返回随机图
PICZ_PORTRAIT = "https://picz.dev/portrait"

# 多分类爬取：每类用 picsum 不同页，保证图片不重复
# 可通过 CRAWL_CATEGORIES 环境变量覆盖，格式：分类1,分类2,分类3
DEFAULT_CATEGORIES = ["picsum.photos", "人像", "枪械模型", "漫威", "其他"]


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


def crawl_images_from_picsum_category(category: str, count: int = 10) -> list[dict]:
    """从 Picsum 按页爬取，打上指定分类（不同分类用不同页范围，减少重复）"""
    items = []
    try:
        # 按分类名 hash 选页范围，保证每类有不同图片
        base = abs(hash(category)) % 40
        page = base + random.randint(0, 9)
        url = f"{PICSUM_API_BASE}?page={page}&limit={count}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        for i, item in enumerate(data[:count]):
            items.append({
                "id": f"{category}_{item.get('id', i)}_{base}",
                "url": item.get("download_url", ""),
                "category": category,
            })
    except Exception:
        pass
    return items if items else [{"id": "", "url": "", "category": category}]


def crawl_images_from_picz(count: int = 15) -> list[dict]:
    """从 picz.dev 爬取人像图片（分类=人像）"""
    source = "人像"
    items = []
    try:
        seen = set()
        for i in range(count):
            r = requests.get(PICZ_PORTRAIT, allow_redirects=True, timeout=15)
            if r.status_code == 200 and r.url and r.url not in seen:
                seen.add(r.url)
                items.append({
                    "id": f"picz_{i}_{hash(r.url) & 0x7FFFFFFF}",
                    "url": r.url,
                    "category": source,
                })
    except Exception:
        pass
    return items if items else [{"id": "", "url": "", "category": source}]


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


def _category_to_filename(category: str) -> str:
    """分类名转安全文件名"""
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in category)
    return safe or "未分类"


def _get_category_files() -> list[Path]:
    """获取所有分类 JSON 文件（data/分类.json）"""
    DATA_DIR.mkdir(exist_ok=True)
    return sorted(DATA_DIR.glob("*.json"), key=lambda p: p.stem)


def list_sources() -> list[dict]:
    """列出所有数据源（按分类分文件）：{name, path, count}"""
    result = []
    for path in _get_category_files():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data) if isinstance(data, list) else 0
        except Exception:
            count = 0
        result.append({"name": path.stem, "path": str(path), "count": count})
    return result


def _get_category_path(category: str) -> Path:
    """获取某分类的 JSON 文件路径"""
    return DATA_DIR / f"{_category_to_filename(category)}.json"


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
    """从 JSON 加载。source_name=分类名，如 人像、漫威"""
    if path is None:
        if source_name:
            p = _get_category_path(source_name)
        else:
            sources = list_sources()
            p = DATA_DIR / f"{sources[0]['name']}.json" if sources else None
    else:
        p = Path(path) if isinstance(path, str) else path
    if p is None or not p.exists():
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


def _get_crawl_categories() -> list[str]:
    """获取要爬取的分类列表"""
    env = os.environ.get("CRAWL_CATEGORIES", "")
    if env:
        return [c.strip() for c in env.split(",") if c.strip()]
    return DEFAULT_CATEGORIES


def _load_crawl_urls_config() -> list[tuple[str, str]]:
    """加载指定网站配置：优先 CRAWL_URLS 环境变量，否则读 data/crawl_urls.txt"""
    env = os.environ.get("CRAWL_URLS", "").strip()
    if env:
        pairs = []
        for part in env.split(","):
            part = part.strip()
            if "|" in part:
                url, cat = part.split("|", 1)
                url, cat = url.strip(), cat.strip()
                if url and cat:
                    pairs.append((url, cat))
        return pairs
    # 从配置文件读取
    cfg = DATA_DIR / "crawl_urls.txt"
    if not cfg.exists():
        return []
    pairs = []
    with open(cfg, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                url, cat = line.split("|", 1)
                url, cat = url.strip(), cat.strip()
                if url and cat:
                    pairs.append((url, cat))
    return pairs


def crawl_images_from_custom_urls() -> list[dict]:
    """从指定网站抓图（CRAWL_URLS 或 data/crawl_urls.txt）"""
    pairs = _load_crawl_urls_config()
    if not pairs:
        return []
    items = []
    for url, category in pairs:
        try:
            sub = crawl_images_from_html(url)
            for x in sub:
                if x.get("url"):
                    x["category"] = category
                    items.append(x)
        except Exception:
            pass
    return items


def _dedupe_by_url(items: list[dict]) -> list[dict]:
    """按 URL 去重，保留首次出现的"""
    seen = set()
    out = []
    for x in items:
        url = (x.get("url") or "").strip()
        if url and url not in seen:
            seen.add(url)
            out.append(_normalize_item(x))
    return out


def _save_category(category: str, new_items: list[dict], accumulate: bool) -> list[dict]:
    """爬取某分类并存入对应 JSON 文件（按 URL 去重）"""
    path = _get_category_path(category)
    valid = [x for x in new_items if x.get("url")]
    if not valid:
        return load_from_json(source_name=category)

    if not accumulate:
        deduped = _dedupe_by_url(valid)
        save_to_json(deduped, path)
        return deduped

    existing = load_from_json(path=path)
    seen_urls = {(x.get("url") or "").strip() for x in existing if x.get("url")}
    merged = existing.copy()
    for item in valid:
        url = (item.get("url") or "").strip()
        if url and url not in seen_urls:
            merged.append(_normalize_item(item))
            seen_urls.add(url)

    merged = _dedupe_by_url(merged)  # 对已有数据也去重
    if len(merged) > MAX_PER_FILE:
        merged = merged[-MAX_PER_FILE:]
    save_to_json(merged, path)
    return merged


def crawl_and_save(use_api: bool = True, accumulate: bool = None) -> list[dict]:
    """按分类分别爬取、分别存 JSON。人像→人像.json，漫威→漫威.json"""
    if accumulate is None:
        accumulate = os.environ.get("ACCUMULATE_IMAGES", "true").lower() == "true"
    all_items = []

    if use_api:
        # 自定义网站：每 url|分类 单独存
        for url, category in _load_crawl_urls_config():
            try:
                sub = crawl_images_from_html(url)
                for x in sub:
                    if x.get("url"):
                        x["category"] = category
                items = [x for x in sub if x.get("url")]
                if items:
                    merged = _save_category(category, items, accumulate)
                    all_items.extend(merged)
            except Exception:
                pass

        # 内置分类：每类单独爬、单独存
        for cat in _get_crawl_categories():
            if cat == "picsum.photos":
                items = crawl_images_from_api()
            elif cat == "人像":
                items = crawl_images_from_picz()
            else:
                items = crawl_images_from_picsum_category(cat, count=8)
            if items:
                merged = _save_category(cat, items, accumulate)
                all_items.extend(merged)
    else:
        items = crawl_images_from_html()
        if items:
            cat = items[0].get("category", "未分类") if items else "未分类"
            all_items = _save_category(cat, items, accumulate)

    return all_items

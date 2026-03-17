# -*- coding: utf-8 -*-
"""简单爬虫 - 可配置爬取目标"""
import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# 默认：quotes.toscrape.com 专为爬虫练习设计，结构清晰
DEFAULT_URL = "https://quotes.toscrape.com/"


def crawl(url: str = None) -> list[dict]:
    """
    爬取页面，返回 {title, link, meta} 列表
    """
    url = url or os.getenv("CRAWL_URL", DEFAULT_URL)
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")

        items = []
        # quotes.toscrape.com 格式（名言+作者+标签）
        if "toscrape" in url:
            for q in soup.select("div.quote")[:20]:
                text = q.select_one("span.text")
                author = q.select_one("small.author")
                tags = q.select("a.tag")
                items.append({
                    "title": text.get_text(strip=True) if text else "",
                    "link": url,
                    "meta": f"—— {author.get_text(strip=True)}" if author else "",
                })
        # Hacker News 格式
        elif "ycombinator" in url:
            for a in soup.select(".titleline > a")[:15]:
                href = a.get("href", "#")
                items.append({"title": a.get_text(strip=True), "link": urljoin(url, href), "meta": ""})
        else:
            for a in soup.find_all("a", href=True)[:20]:
                title = a.get_text(strip=True)
                if title and len(title) > 2:
                    items.append({"title": title[:80], "link": urljoin(url, a["href"]), "meta": ""})

        return items
    except Exception as e:
        return [{"title": f"爬取失败: {e}", "link": "#", "meta": ""}]

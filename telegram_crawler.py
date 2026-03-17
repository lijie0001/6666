# -*- coding: utf-8 -*-
"""
Telegram 群组爬虫 - 监控源群组新消息并转发到目标群组

需要：Telethon 用户客户端，从 my.telegram.org 获取 API_ID、API_HASH
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, events

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")
PROXY = os.getenv("TELEGRAM_PROXY")

def _parse_group(v: str):
    v = v.strip()
    if not v:
        return ""
    if v.lstrip("-").isdigit():
        return int(v)
    return v

SOURCE_GROUP = _parse_group(os.getenv("CRAWLER_SOURCE", ""))
TARGET_GROUP = _parse_group(os.getenv("CRAWLER_TARGET", ""))


def parse_proxy(proxy_str: str) -> tuple | None:
    if not proxy_str:
        return None
    s = proxy_str.strip()
    if s.startswith("socks5://"):
        p = s.replace("socks5://", "").split(":")
        return ("socks5", p[0], int(p[1]) if len(p) > 1 else 1080)
    if s.startswith("http://"):
        p = s.replace("http://", "").split(":")
        return ("http", p[0], int(p[1]) if len(p) > 1 else 7890)
    return None


async def run():
    if not all([API_ID, API_HASH, PHONE, SOURCE_GROUP, TARGET_GROUP]):
        print("请配置 .env：")
        print("  TELEGRAM_API_ID=    # my.telegram.org")
        print("  TELEGRAM_API_HASH=  # my.telegram.org")
        print("  TELEGRAM_PHONE=     # +8613800138000")
        print("  CRAWLER_SOURCE=     # 源群组 ID 或 @用户名")
        print("  CRAWLER_TARGET=     # 目标群组 ID 或 @用户名")
        return

    proxy = parse_proxy(PROXY) if PROXY else None
    client = TelegramClient("crawler_session", API_ID, API_HASH, proxy=proxy)

    await client.start(phone=PHONE)

    @client.on(events.NewMessage(chats=SOURCE_GROUP))
    async def handler(event):
        msg = event.message
        if not msg.text and not msg.media:
            return
        try:
            sender = await msg.get_sender()
            name = getattr(sender, "first_name", "") or getattr(sender, "title", "未知")
            time_str = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else ""
            header = f"📥 [{name}] {time_str}\n"
            text = msg.text or "[媒体]"
            full = header + (text[:4000] + "..." if len(text) > 4000 else text)
            await client.send_message(TARGET_GROUP, full)
            if msg.media:
                await client.send_message(TARGET_GROUP, file=msg.media)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 已转发: {text[:40]}...")
        except Exception as e:
            print(f"转发失败: {e}")

    print("爬虫已启动，监控源群组新消息并转发到目标群组")
    print(f"源: {SOURCE_GROUP} -> 目标: {TARGET_GROUP}")
    print("按 Ctrl+C 停止\n")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(run())

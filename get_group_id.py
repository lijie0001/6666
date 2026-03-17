# -*- coding: utf-8 -*-
"""
获取 Telegram 群组 ID - 运行后列出你加入的群组及 ID
"""
import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()
API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
PHONE = os.getenv("TELEGRAM_PHONE", "")
PROXY = os.getenv("TELEGRAM_PROXY")


def parse_proxy(s):
    if not s:
        return None
    s = s.strip()
    if s.startswith("socks5://"):
        p = s.replace("socks5://", "").split(":")
        return ("socks5", p[0], int(p[1]) if len(p) > 1 else 1080)
    if s.startswith("http://"):
        p = s.replace("http://", "").split(":")
        return ("http", p[0], int(p[1]) if len(p) > 1 else 7890)
    return None


async def main():
    if not all([API_ID, API_HASH, PHONE]):
        print("请先配置 .env: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
        return

    proxy = parse_proxy(PROXY) if PROXY else None
    client = TelegramClient("crawler_session", API_ID, API_HASH, proxy=proxy)
    await client.start(phone=PHONE)

    print("你的群组列表：\n")
    async for d in client.iter_dialogs():
        if d.is_group or d.is_channel:
            print(f"  {d.title}")
            print(f"    ID: {d.id}")
            print(f"    用户名: @{d.entity.username}" if d.entity.username else "    用户名: 无")
            print()

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

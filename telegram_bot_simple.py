# -*- coding: utf-8 -*-
"""
极简 Telegram 机器人 - 使用 requests，不依赖 httpx
用于排查 Python 3.14 + httpx 的兼容问题
"""
import os
import time
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PROXY = os.getenv("TELEGRAM_PROXY")  # 如 http://127.0.0.1:7890
BASE = f"https://api.telegram.org/bot{TOKEN}"

def get_proxies():
    return {"https": PROXY, "http": PROXY} if PROXY else None

def main():
    if not TOKEN:
        print("错误：请配置 TELEGRAM_BOT_TOKEN")
        return

    proxies = get_proxies()
    print("测试连接...")
    try:
        r = requests.get(f"{BASE}/getMe", proxies=proxies, timeout=15)
        r.raise_for_status()
        print(f"连接成功！机器人: @{r.json()['result']['username']}")
    except Exception as e:
        print(f"连接失败: {e}")
        print("\n若用代理，在 .env 取消注释: TELEGRAM_PROXY=http://127.0.0.1:7890")
        return

    print("机器人运行中，按 Ctrl+C 停止\n")
    offset = 0
    while True:
        try:
            r = requests.get(
                f"{BASE}/getUpdates",
                params={"offset": offset, "timeout": 30},
                proxies=proxies,
                timeout=35,
            )
            r.raise_for_status()
            data = r.json()
            for u in data.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message")
                if not msg:
                    continue
                text = msg.get("text", "")
                chat_id = msg["chat"]["id"]

                if text == "/start":
                    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": "你好！我是你的机器人～"}, proxies=proxies, timeout=10)
                elif text == "/help":
                    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": "/start - 开始\n/help - 帮助"}, proxies=proxies, timeout=10)
                elif text:
                    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": text}, proxies=proxies, timeout=10)
        except KeyboardInterrupt:
            print("\n已停止")
            break
        except Exception as e:
            print(f"错误: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

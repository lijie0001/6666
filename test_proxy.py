# -*- coding: utf-8 -*-
"""测试代理是否能连接 Telegram API"""
import urllib.request
import ssl

PROXY = "http://127.0.0.1:7890"
URL = "https://api.telegram.org"

def test():
    proxy_handler = urllib.request.ProxyHandler({"https": PROXY, "http": PROXY})
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    opener = urllib.request.build_opener(
        proxy_handler,
        urllib.request.HTTPSHandler(context=ctx)
    )
    try:
        resp = opener.open(URL, timeout=10)
        print("[OK] 代理连接成功！可以访问 Telegram API")
        return True
    except Exception as e:
        print(f"[失败] {e}")
        print("\n可能原因：")
        print("  1. Clash 的 HTTP 代理与 Python 3.14 存在 SSL 兼容问题")
        print("  2. 尝试：Clash 开启「系统代理」或「TUN 模式」让程序走系统代理")
        print("  3. 或使用 VPN 全局模式，再在 .env 中删除 TELEGRAM_PROXY 行")
        return False

if __name__ == "__main__":
    test()

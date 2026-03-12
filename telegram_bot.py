# -*- coding: utf-8 -*-
"""
Telegram 机器人
配置 .env: TELEGRAM_BOT_TOKEN, 可选 TELEGRAM_PROXY（国内需代理）
"""

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PROXY = os.getenv("TELEGRAM_PROXY")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text("你好！我是你的机器人，发送任意文字我会回复你～")


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    await update.message.reply_text(
        "可用命令：\n"
        "/start - 开始\n"
        "/help - 帮助\n"
        "发送任意文字 - 我会原样回复"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """回复用户发的文字"""
    await update.message.reply_text(update.message.text)


def main():
    if not TOKEN:
        print("错误：请先在 .env 文件中配置 TELEGRAM_BOT_TOKEN")
        return

    # 配置请求：代理（国内需配置）、超时  
    request = HTTPXRequest(
        connect_timeout=60,
        read_timeout=60,
        proxy=PROXY if PROXY else None,
    )
    app = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("机器人已启动，按 Ctrl+C 停止")
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"\n启动失败: {e}")
        print("\n可能原因：")
        print("  1. 国内网络需配置代理，在 .env 添加: TELEGRAM_PROXY=http://127.0.0.1:7890")
        print("  2. Token 无效，请从 @BotFather 重新获取")
        print("  3. 检查代理软件(Clash/V2Ray)是否已开启")


if __name__ == "__main__":
    main()

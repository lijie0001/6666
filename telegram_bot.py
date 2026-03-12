# -*- coding: utf-8 -*-
"""
Telegram 机器人 - AI 智能回复
配置 .env: TELEGRAM_BOT_TOKEN, OPENAI_API_KEY
"""

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PROXY = os.getenv("TELEGRAM_PROXY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 对话历史（按用户维护，简单实现）
user_history: dict[int, list[dict]] = {}
MAX_HISTORY = 10


async def get_ai_reply(user_id: int, text: str) -> str:
    """调用 AI 获取回复"""
    if not OPENAI_API_KEY:
        return text  # 无 API Key 时原样回复

    try:
        from openai import OpenAI

        kwargs = {"api_key": OPENAI_API_KEY}
        if os.getenv("OPENAI_BASE_URL"):
            kwargs["base_url"] = os.getenv("OPENAI_BASE_URL")
        client = OpenAI(**kwargs)

        # 获取历史
        history = user_history.get(user_id, [])
        messages = history + [{"role": "user", "content": text}]

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": "你是一个友好、有用的助手，用中文简洁回复。"},
                *messages,
            ],
            max_tokens=500,
        )

        reply = response.choices[0].message.content

        # 更新历史
        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": reply})
        user_history[user_id] = history[-MAX_HISTORY * 2 :]

        return reply

    except Exception as e:
        return f"回复出错: {str(e)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text(
        "你好！我是 AI 助手，可以回答你的问题。\n"
        "直接发送文字即可，我会智能回复～"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    await update.message.reply_text(
        "可用命令：\n"
        "/start - 开始\n"
        "/help - 帮助\n"
        "/clear - 清除对话历史\n"
        "发送任意文字 - AI 智能回复"
    )


async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """清除对话历史"""
    user_id = update.effective_user.id
    user_history.pop(user_id, None)
    await update.message.reply_text("已清除对话历史。")


async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI 回复"""
    text = update.message.text
    user_id = update.effective_user.id

    # 发送"正在思考"提示
    thinking = await update.message.reply_text("思考中...")

    reply = await get_ai_reply(user_id, text)

    # 删除"思考中"并发送回复
    await thinking.delete()
    await update.message.reply_text(reply)


def main():
    if not TOKEN:
        print("错误：请配置 TELEGRAM_BOT_TOKEN")
        return

    if not OPENAI_API_KEY:
        print("提示：未配置 OPENAI_API_KEY，将使用原样回复模式")

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
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

    print("AI 机器人已启动，按 Ctrl+C 停止")
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"\n启动失败: {e}")


if __name__ == "__main__":
    main()

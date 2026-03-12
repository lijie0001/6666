# Telegram 机器人部署指南

## 方式一：Railway（推荐，免费额度）

### 1. 注册 Railway

- 打开 https://railway.app
- 用 GitHub 登录

### 2. 把代码推到 GitHub

```powershell
cd d:\python
git init
git add telegram_bot.py requirements.txt Procfile runtime.txt
git add .gitignore
git commit -m "Telegram bot"
```

在 GitHub 创建新仓库，然后：

```powershell
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

### 3. 在 Railway 部署

1. 登录 https://railway.app
2. 点击 **New Project** → **Deploy from GitHub repo**
3. 选择你的仓库
4. 进入项目 → **Variables** → 添加环境变量：
   - `TELEGRAM_BOT_TOKEN` = 你的 Bot Token
   - `OPENAI_API_KEY` = 你的 OpenAI API Key（用于 AI 智能回复）
5. 点击 **Settings** → **Service** → 确认 **Start Command** 为 `python telegram_bot.py`（或留空，Railway 会用 Procfile）
6. 若需指定为 Worker：在 **Settings** 中把 Service 类型设为 **Worker**（部分模板会自动识别 Procfile 的 worker）

### 4. 部署完成

机器人会在 Railway 的服务器上 24 小时运行，无需代理。

---

## 方式二：Render

1. 打开 https://render.com，用 GitHub 登录
2. **New** → **Background Worker**
3. 连接 GitHub 仓库
4. 配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python telegram_bot.py`
5. **Environment** 添加 `TELEGRAM_BOT_TOKEN`
6. 免费版 15 分钟无请求会休眠，可能不适合需要常驻的机器人

---

## 方式三：自己的 VPS

若有海外 VPS（如 Vultr、DigitalOcean）：

```bash
# 安装 Python
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# 上传代码后
cd /path/to/your/bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 设置环境变量
export TELEGRAM_BOT_TOKEN=你的Token

# 后台运行（用 nohup 或 systemd）
nohup python telegram_bot.py > bot.log 2>&1 &
```

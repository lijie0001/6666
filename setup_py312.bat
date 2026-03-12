@echo off
chcp 65001 >nul
echo 使用 Python 3.12 创建新虚拟环境...
echo.

where py -3.12 >nul 2>&1
if %errorlevel% neq 0 (
    echo 未找到 Python 3.12，请先安装：
    echo   1. 打开 https://www.python.org/downloads/
    echo   2. 下载 Python 3.12.x
    echo   3. 安装时勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo 创建 venv312...
py -3.12 -m venv venv312

echo.
echo 激活并安装依赖...
call venv312\Scripts\activate.bat
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo 完成！运行机器人：
echo   venv312\Scripts\activate
echo   python telegram_bot.py
pause

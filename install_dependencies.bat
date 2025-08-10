@echo off
title MP3 Uploader - 安装依赖

echo ====================================================
echo  正在为 MP3 快捷上传工具安装必要的 Python 依赖
echo ====================================================
echo.

rem 检查 Python 是否在 PATH 中
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 Python。请确保已安装 Python 3.6+ 并将其添加到系统 PATH。
    echo 建议从 https://www.python.org/downloads/ 下载并安装。
    pause
    goto :eof
)

echo 1. 正在创建 Python 虚拟环境 (venv)...
python -m venv venv
if %errorlevel% neq 0 (
    echo 错误：创建虚拟环境失败。
    echo 可能是权限问题，或者 Python 安装不完整。
    pause
    goto :eof
)
echo 虚拟环境创建成功。

echo.
echo 2. 正在激活虚拟环境...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo 错误：激活虚拟环境失败。
    pause
    goto :eof
)
echo 虚拟环境已激活。

echo.
echo 3. 正在安装 Flask 库...
pip install Flask
if %errorlevel% neq 0 (
    echo 错误：安装 Flask 失败。
    echo 请检查您的网络连接，或尝试手动运行 'pip install Flask'。
    deactivate >nul 2>&1
    pause
    goto :eof
)
echo Flask 安装成功！

echo.
echo 4. 正在退出虚拟环境...
deactivate >nul 2>&1
echo 虚拟环境已退出。

echo.
echo ====================================================
echo  所有依赖已成功安装！
echo  现在您可以运行服务器了：
echo  cd MP3
echo  venv\Scripts\activate
echo  python server.py
echo ====================================================
echo.
pause
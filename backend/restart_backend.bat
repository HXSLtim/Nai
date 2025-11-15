@echo off
echo 正在重启后端服务...
echo.

REM 杀掉可能占用8000端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 发现占用8000端口的进程: %%a
    taskkill /F /PID %%a
)

echo.
echo 等待端口释放...
timeout /t 2 /nobreak > nul

echo.
echo 启动新的后端服务...
cd /d "%~dp0"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause

@echo off
echo 正在查找占用8000端口的所有进程...
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 发现进程: %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo 清理完成！
timeout /t 2 /nobreak > nul

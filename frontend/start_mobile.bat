@echo off
echo 🚀 启动AI小说创作系统前端服务（移动端模式）
echo.

REM 获取本机IP地址
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set LOCAL_IP=%%b
        goto :found
    )
)
:found

echo 📱 移动端访问地址: http://%LOCAL_IP%:3000
echo 🖥️  本地访问地址: http://localhost:3000
echo.
echo 移动端连接说明:
echo 1. 确保手机和电脑在同一WiFi网络
echo 2. 在手机浏览器中访问上述移动端地址
echo 3. 如果页面加载但无法登录，请检查后端服务
echo ================================================
echo.

REM 启动Next.js开发服务器，监听所有网络接口
npm run dev -- --hostname 0.0.0.0

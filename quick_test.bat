@echo off
echo 🚀 快速API连接测试
echo.

echo 1. 测试后端健康检查...
curl -s http://192.168.31.101:8000/api/health
echo.
echo.

echo 2. 测试后端ping...
curl -s http://192.168.31.101:8000/api/ping
echo.
echo.

echo 3. 测试CORS预检请求...
curl -s -X OPTIONS -H "Origin: http://198.18.0.1:3000" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: Content-Type" http://192.168.31.101:8000/api/auth/login
echo.
echo.

echo 4. 测试登录接口结构...
curl -s -X POST -H "Content-Type: application/json" -d "{\"username\":\"test\",\"password\":\"test\"}" http://192.168.31.101:8000/api/auth/login
echo.
echo.

echo ================================================
echo 如果看到JSON响应，说明后端运行正常
echo 如果看到错误或无响应，请检查：
echo 1. 后端服务是否启动 (python start_mobile.py)
echo 2. 防火墙设置
echo 3. 网络连接
echo ================================================
pause

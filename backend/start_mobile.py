#!/usr/bin/env python3
"""
移动端访问启动脚本
确保后端服务可以被局域网内的设备访问
"""

import uvicorn
import socket
from loguru import logger

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 连接到一个远程地址来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    
    logger.info("🚀 启动AI小说创作系统后端服务")
    logger.info(f"📱 移动端访问地址: http://{local_ip}:8000")
    logger.info(f"🖥️  本地访问地址: http://localhost:8000")
    logger.info(f"📚 API文档地址: http://{local_ip}:8000/docs")
    logger.info("=" * 50)
    logger.info("移动端连接说明:")
    logger.info("1. 确保手机和电脑在同一WiFi网络")
    logger.info("2. 在手机浏览器中访问上述移动端地址")
    logger.info("3. 如果无法访问，请检查防火墙设置")
    logger.info("=" * 50)
    
    # 启动服务，监听所有网络接口
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,
        reload=True,
        log_level="info"
    )

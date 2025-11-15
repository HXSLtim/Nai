"""测试一致性检查API是否可用"""
import requests
import json

# 测试 OPTIONS 请求
print("测试 OPTIONS 请求...")
try:
    response = requests.options("http://192.168.31.101:8000/api/consistency/check-stream")
    print(f"OPTIONS 状态码: {response.status_code}")
    print(f"允许的方法: {response.headers.get('Allow', 'N/A')}")
except Exception as e:
    print(f"OPTIONS 请求失败: {e}")

print("\n" + "="*50 + "\n")

# 测试 POST 请求
print("测试 POST 请求...")
try:
    payload = {
        "novel_id": 1,
        "chapter": 1,
        "content": "测试内容",
        "current_day": 1
    }
    response = requests.post(
        "http://192.168.31.101:8000/api/consistency/check-stream",
        json=payload,
        stream=True,
        timeout=5
    )
    print(f"POST 状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    if response.status_code == 200:
        print("\n接收到的前几个事件:")
        count = 0
        for line in response.iter_lines():
            if line:
                print(line.decode('utf-8'))
                count += 1
                if count >= 5:
                    break
    else:
        print(f"响应内容: {response.text}")
        
except Exception as e:
    print(f"POST 请求失败: {e}")

print("\n" + "="*50 + "\n")

# 检查 /docs 是否列出了这个路由
print("检查 API 文档...")
try:
    response = requests.get("http://192.168.31.101:8000/openapi.json")
    if response.status_code == 200:
        openapi_spec = response.json()
        if "/api/consistency/check-stream" in openapi_spec.get("paths", {}):
            print("✓ 路由已在 OpenAPI 规范中注册")
            methods = list(openapi_spec["paths"]["/api/consistency/check-stream"].keys())
            print(f"  支持的方法: {methods}")
        else:
            print("✗ 路由未在 OpenAPI 规范中找到")
            print(f"  可用的一致性相关路由: {[p for p in openapi_spec.get('paths', {}).keys() if 'consistency' in p]}")
    else:
        print(f"无法获取 OpenAPI 规范: {response.status_code}")
except Exception as e:
    print(f"检查 API 文档失败: {e}")

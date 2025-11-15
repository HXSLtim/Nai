"""测试新添加的路由"""
import requests

print("=" * 60)
print("测试一致性检查路由")
print("=" * 60)

# 测试 GET /test 路由
print("\n1. 测试 GET /api/consistency/test")
try:
    response = requests.get("http://192.168.31.101:8000/api/consistency/test")
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"   响应: {response.json()}")
    else:
        print(f"   错误: {response.text}")
except Exception as e:
    print(f"   异常: {e}")

# 测试 POST /check-stream 路由
print("\n2. 测试 POST /api/consistency/check-stream")
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
    print(f"   状态码: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    
    if response.status_code == 200:
        print("   接收到的前几个事件:")
        count = 0
        for line in response.iter_lines():
            if line:
                print(f"     {line.decode('utf-8')}")
                count += 1
                if count >= 5:
                    break
    else:
        print(f"   错误: {response.text}")
        
except Exception as e:
    print(f"   异常: {e}")

# 再次检查 OpenAPI 规范
print("\n3. 检查 OpenAPI 规范")
try:
    response = requests.get("http://192.168.31.101:8000/openapi.json")
    if response.status_code == 200:
        spec = response.json()
        consistency_paths = [p for p in spec.get("paths", {}).keys() if 'consistency' in p]
        print(f"   一致性检查相关路径: {consistency_paths}")
    else:
        print(f"   无法获取 OpenAPI 规范: {response.status_code}")
except Exception as e:
    print(f"   异常: {e}")

print("\n" + "=" * 60)

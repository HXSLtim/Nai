"""检查 /docs 端点返回的 OpenAPI 规范"""
import requests
import json

try:
    response = requests.get("http://192.168.31.101:8000/openapi.json")
    if response.status_code == 200:
        spec = response.json()
        
        print("=" * 60)
        print("OpenAPI 规范中的所有路径：")
        print("=" * 60)
        
        consistency_paths = []
        all_paths = list(spec.get("paths", {}).keys())
        
        for path in sorted(all_paths):
            if 'consistency' in path:
                consistency_paths.append(path)
                methods = list(spec["paths"][path].keys())
                print(f"✓ {path}: {methods}")
        
        print("\n" + "=" * 60)
        print(f"一致性检查相关路径数量: {len(consistency_paths)}")
        print("=" * 60)
        
        if not consistency_paths:
            print("\n⚠️ OpenAPI 规范中没有一致性检查路径！")
            print("\n所有 /api 开头的路径：")
            for path in sorted(all_paths):
                if path.startswith('/api'):
                    methods = list(spec["paths"][path].keys())
                    print(f"  {path}: {methods}")
        
        print("\n" + "=" * 60)
        print(f"总路径数量: {len(all_paths)}")
        print("=" * 60)
        
        # 保存完整规范到文件以便检查
        with open("openapi_spec.json", "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
        print("\n完整 OpenAPI 规范已保存到 openapi_spec.json")
        
    else:
        print(f"无法获取 OpenAPI 规范: HTTP {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"请求失败: {e}")

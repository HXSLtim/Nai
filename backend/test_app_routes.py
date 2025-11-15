"""测试 FastAPI 应用中实际注册的路由"""
import sys
sys.path.insert(0, ".")

from app.main import app

print("=" * 60)
print("FastAPI 应用中实际注册的路由")
print("=" * 60)

consistency_routes = []
all_api_routes = []

for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        path = route.path
        methods = list(route.methods)
        
        if path.startswith('/api'):
            all_api_routes.append(f"{methods} {path}")
        
        if 'consistency' in path:
            consistency_routes.append(f"{methods} {path}")
            print(f"✓ {methods} {path}")

print("\n" + "=" * 60)
print(f"一致性检查路由数量: {len(consistency_routes)}")
print("=" * 60)

if not consistency_routes:
    print("\n⚠️ 警告：应用中没有注册一致性检查路由！")
    print("\n所有 /api 路由：")
    for route in sorted(all_api_routes):
        print(f"  {route}")
else:
    print("\n✓ 一致性检查路由已在应用中注册")

print("\n" + "=" * 60)
print(f"总 API 路由数量: {len(all_api_routes)}")
print("=" * 60)

# 检查 consistency.router 本身
print("\n检查 consistency.router 对象：")
from app.api.routes import consistency
print(f"  router 类型: {type(consistency.router)}")
print(f"  router 中的路由数量: {len(consistency.router.routes)}")
for route in consistency.router.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"    - {list(route.methods)} {route.path}")

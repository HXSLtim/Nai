"""检查FastAPI应用中注册的所有路由"""
import sys
sys.path.insert(0, ".")

from app.main import app

print("=" * 60)
print("FastAPI 应用中注册的所有路由：")
print("=" * 60)

consistency_routes = []
all_routes = []

for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        route_info = f"{list(route.methods)} {route.path}"
        all_routes.append(route_info)
        
        if 'consistency' in route.path:
            consistency_routes.append(route_info)
            print(f"✓ {route_info}")

print("\n" + "=" * 60)
print(f"一致性检查相关路由数量: {len(consistency_routes)}")
print("=" * 60)

if not consistency_routes:
    print("\n⚠️ 警告：没有找到任何一致性检查相关的路由！")
    print("\n所有包含 'api' 的路由：")
    for route in all_routes:
        if 'api' in route:
            print(f"  {route}")
else:
    print("\n✓ 一致性检查路由已正确注册")

print("\n" + "=" * 60)
print(f"总路由数量: {len(all_routes)}")
print("=" * 60)

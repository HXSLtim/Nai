"""测试导入 consistency 模块"""
import sys
sys.path.insert(0, ".")

print("=" * 60)
print("测试导入 consistency 路由模块")
print("=" * 60)

try:
    print("\n1. 导入 consistency 模块...")
    from app.api.routes import consistency
    print("   ✓ 导入成功")
    
    print("\n2. 检查 router 对象...")
    print(f"   router 类型: {type(consistency.router)}")
    print(f"   router 对象: {consistency.router}")
    
    print("\n3. 检查 router 中的路由...")
    if hasattr(consistency.router, 'routes'):
        routes = consistency.router.routes
        print(f"   路由数量: {len(routes)}")
        for route in routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"   - {list(route.methods)} {route.path}")
    else:
        print("   ⚠️ router 没有 routes 属性")
    
    print("\n4. 尝试直接调用测试路由...")
    import asyncio
    result = asyncio.run(consistency.test_consistency_route())
    print(f"   测试路由返回: {result}")
    
except ImportError as e:
    print(f"   ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"   ✗ 其他错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

"""
测试Novel和Chapter API
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api"

# 首先登录获取token
print("=" * 60)
print("步骤1: 用户登录")
print("=" * 60)

login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": "testuser",
        "password": "test123456"
    }
)

if login_response.status_code == 200:
    token_data = login_response.json()
    access_token = token_data["access_token"]
    print(f"[OK] 登录成功，Token: {access_token[:20]}...")
else:
    print(f"[FAIL] 登录失败: {login_response.text}")
    exit(1)

# 设置认证头
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# 测试创建小说
print("\n" + "=" * 60)
print("步骤2: 创建小说")
print("=" * 60)

novel_data = {
    "title": "修仙之路",
    "genre": "玄幻",
    "description": "一个关于少年修仙的故事",
    "worldview": "修仙世界，分为炼气、筑基、金丹、元婴等境界"
}

create_novel_response = requests.post(
    f"{BASE_URL}/novels/",
    headers=headers,
    json=novel_data
)

if create_novel_response.status_code == 201:
    novel = create_novel_response.json()
    novel_id = novel["id"]
    print(f"[OK] 小说创建成功")
    print(f"  ID: {novel_id}")
    print(f"  标题: {novel['title']}")
    print(f"  类型: {novel['genre']}")
else:
    print(f"[FAIL] 创建小说失败: {create_novel_response.text}")
    exit(1)

# 测试获取小说列表
print("\n" + "=" * 60)
print("步骤3: 获取小说列表")
print("=" * 60)

list_novels_response = requests.get(
    f"{BASE_URL}/novels/",
    headers=headers
)

if list_novels_response.status_code == 200:
    novels = list_novels_response.json()
    print(f"[OK] 共有 {len(novels)} 部小说")
    for n in novels:
        print(f"  - {n['title']} (ID: {n['id']})")
else:
    print(f"[FAIL] 获取小说列表失败: {list_novels_response.text}")

# 测试创建章节
print("\n" + "=" * 60)
print("步骤4: 创建章节")
print("=" * 60)

chapter_data = {
    "chapter_number": 1,
    "title": "第一章 初入修仙界",
    "content": "李明是一个十六岁的少年，生活在青云镇。在一次偶然的机会下，他发现了一枚古老的玉佩，从此踏上了修仙之路..."
}

create_chapter_response = requests.post(
    f"{BASE_URL}/novels/{novel_id}/chapters",
    headers=headers,
    json=chapter_data
)

if create_chapter_response.status_code == 201:
    chapter = create_chapter_response.json()
    chapter_id = chapter["id"]
    print(f"[OK] 章节创建成功")
    print(f"  ID: {chapter_id}")
    print(f"  章节号: {chapter['chapter_number']}")
    print(f"  标题: {chapter['title']}")
    print(f"  字数: {chapter['word_count']}")
else:
    print(f"[FAIL] 创建章节失败: {create_chapter_response.text}")
    exit(1)

# 测试获取章节列表
print("\n" + "=" * 60)
print("步骤5: 获取章节列表")
print("=" * 60)

list_chapters_response = requests.get(
    f"{BASE_URL}/novels/{novel_id}/chapters",
    headers=headers
)

if list_chapters_response.status_code == 200:
    chapters = list_chapters_response.json()
    print(f"[OK] 小说共有 {len(chapters)} 个章节")
    for ch in chapters:
        print(f"  - 第{ch['chapter_number']}章: {ch['title']} ({ch['word_count']}字)")
else:
    print(f"[FAIL] 获取章节列表失败: {list_chapters_response.text}")

# 测试更新章节
print("\n" + "=" * 60)
print("步骤6: 更新章节")
print("=" * 60)

update_data = {
    "content": chapter_data["content"] + "\n\n李明惊讶地发现，这枚玉佩竟然蕴含着强大的灵力！"
}

update_chapter_response = requests.put(
    f"{BASE_URL}/novels/{novel_id}/chapters/{chapter_id}",
    headers=headers,
    json=update_data
)

if update_chapter_response.status_code == 200:
    updated_chapter = update_chapter_response.json()
    print(f"[OK] 章节更新成功")
    print(f"  新字数: {updated_chapter['word_count']}")
else:
    print(f"[FAIL] 更新章节失败: {update_chapter_response.text}")

# 测试获取单个章节
print("\n" + "=" * 60)
print("步骤7: 获取章节详情")
print("=" * 60)

get_chapter_response = requests.get(
    f"{BASE_URL}/novels/{novel_id}/chapters/{chapter_id}",
    headers=headers
)

if get_chapter_response.status_code == 200:
    chapter_detail = get_chapter_response.json()
    print(f"[OK] 章节详情:")
    print(f"  章节号: {chapter_detail['chapter_number']}")
    print(f"  标题: {chapter_detail['title']}")
    print(f"  内容: {chapter_detail['content'][:50]}...")
else:
    print(f"[FAIL] 获取章节详情失败: {get_chapter_response.text}")

print("\n" + "=" * 60)
print("[SUCCESS] 所有API测试完成！")
print("=" * 60)

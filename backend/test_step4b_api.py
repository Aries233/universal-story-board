"""
Universal Story Board - Step 4-B API 测试脚本
测试章节管理和资产管理 API
"""
import requests
import json
import sys

# API 基础 URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 创建测试项目并获取 ID
project_id = None


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(f"🔍 {title}")
    print("=" * 80)


def print_response(response, title="响应"):
    """打印响应结果"""
    print(f"\n📋 {title}")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data
    except:
        print(f"响应文本: {response.text}")
        return None


def test_create_test_project():
    """创建测试项目"""
    global project_id

    print_section("创建测试项目")

    try:
        payload = {
            "name": "测试项目 - 章节与资产",
            "description": "用于测试章节和资产 API 的项目",
            "workflow_mode": "A"
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(
            f"{API_BASE}/projects",
            json=payload
        )

        data = print_response(response, "创建项目响应")

        if response.status_code == 201 and data:
            project_id = data['id']
            print(f"\n✅ 项目创建成功，ID: {project_id}")
            return True

        return False
    except Exception as e:
        print(f"❌ 创建项目失败: {e}")
        return False


def test_list_chapters():
    """测试获取章节列表"""
    print_section("测试获取章节列表")

    try:
        response = requests.get(
            f"{API_BASE}/chapters",
            params={"project_id": project_id}
        )

        data = print_response(response, "章节列表")

        if response.status_code == 200 and data:
            print(f"\n✅ 总章节数: {data['total']}")
            for chapter in data['items']:
                print(f"   • 第 {chapter['chapter_number']} 章: {chapter['title']}")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 获取章节列表失败: {e}")
        return False


def test_create_chapter():
    """测试创建章节"""
    print_section("测试创建章节")

    try:
        payload = {
            "project_id": project_id,
            "chapter_number": 1,
            "title": "第一章：穿越",
            "original_text": "林峰睁开眼睛，发现自己躺在一张古老的木床上..."
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(
            f"{API_BASE}/chapters",
            json=payload
        )

        data = print_response(response, "创建章节响应")

        if response.status_code == 201 and data:
            print(f"\n✅ 章节创建成功，ID: {data['id']}")

        return response.status_code == 201
    except Exception as e:
        print(f"❌ 创建章节失败: {e}")
        return False


def test_batch_create_chapters():
    """测试批量创建章节"""
    print_section("测试批量创建章节")

    try:
        payload = {
            "project_id": project_id,
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "第一章：穿越",
                    "original_text": "林峰睁开眼睛，发现自己躺在一张古老的木床上..."
                },
                {
                    "chapter_number": 2,
                    "title": "第二章：初遇",
                    "original_text": "他走出房间，来到了一个陌生的大厅..."
                },
                {
                    "chapter_number": 3,
                    "title": "第三章：挑战",
                    "original_text": "大厅中央站着一个神秘的老人，向他招手..."
                }
            ]
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(
            f"{API_BASE}/chapters/batch",
            json=payload
        )

        data = print_response(response, "批量创建章节响应")

        if response.status_code == 201 and data:
            print(f"\n✅ 批量创建成功，共 {len(data)} 章")

        return response.status_code == 201
    except Exception as e:
        print(f"❌ 批量创建章节失败: {e}")
        return False


def test_update_chapter():
    """测试更新章节"""
    print_section("测试更新章节")

    try:
        # 先获取第一个章节的 ID
        response = requests.get(
            f"{API_BASE}/chapters",
            params={"project_id": project_id, "limit": 1}
        )

        if response.status_code != 200:
            print("❌ 获取章节列表失败，无法更新")
            return False

        data = response.json()
        if not data['items']:
            print("❌ 没有可更新的章节")
            return False

        chapter_id = data['items'][0]['id']

        payload = {
            "title": "第一章：穿越（更新版）",
            "status": "processing"
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.put(
            f"{API_BASE}/chapters/{chapter_id}",
            json=payload
        )

        data = print_response(response, "更新章节响应")

        if response.status_code == 200:
            print(f"\n✅ 章节更新成功")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 更新章节失败: {e}")
        return False


def test_list_assets():
    """测试获取资产列表"""
    print_section("测试获取资产列表")

    try:
        response = requests.get(
            f"{API_BASE}/assets",
            params={"project_id": project_id}
        )

        data = print_response(response, "资产列表")

        if response.status_code == 200 and data:
            print(f"\n✅ 总资产数: {data['total']}")
            for asset in data['items']:
                print(f"   • {asset['name']} ({asset['asset_type']})")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 获取资产列表失败: {e}")
        return False


def test_create_character_asset():
    """测试创建角色资产"""
    print_section("测试创建角色资产")

    try:
        payload = {
            "project_id": project_id,
            "asset_type": "character",
            "name": "林峰",
            "description": "穿越到唐朝的现代青年，机智谨慎，性格温和",
            "tags": ["主角", "穿越者", "书生"],
            "age": "青年",
            "personality": ["机智", "谨慎", "温和"],
            "appearance": "清秀书生，着青衫，面容白净",
            "costume": "青色长衫，白色内衬",
            "props": ["卷轴", "毛笔"],
            "prompts": {
                "portrait": "中国古代书生，青衫，清秀面容，唐朝风格...",
                "full_body": "中国古代书生全身像，青色长衫，手持毛笔，唐朝风格..."
            }
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(
            f"{API_BASE}/assets",
            json=payload
        )

        data = print_response(response, "创建角色资产响应")

        if response.status_code == 201 and data:
            print(f"\n✅ 角色资产创建成功，ID: {data['id']}")

        return response.status_code == 201
    except Exception as e:
        print(f"❌ 创建角色资产失败: {e}")
        return False


def test_create_scene_asset():
    """测试创建场景资产"""
    print_section("测试创建场景资产")

    try:
        payload = {
            "project_id": project_id,
            "asset_type": "scene",
            "name": "翰林院",
            "description": "唐朝翰林院，宽敞明亮，书案林立，文房四宝摆放整齐",
            "tags": ["室内", "古代", "书院"],
            "time_of_day": "白天",
            "atmosphere": "宁静、典雅",
            "environment": "书案、卷轴、文房四宝、屏风",
            "prompts": {
                "wide_shot": "唐朝翰林院全景，宽敞明亮，书案林立，古代建筑风格...",
                "detail": "翰林院内书案特写，卷轴、文房四宝、毛笔、砚台..."
            }
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(
            f"{API_BASE}/assets",
            json=payload
        )

        data = print_response(response, "创建场景资产响应")

        if response.status_code == 201 and data:
            print(f"\n✅ 场景资产创建成功，ID: {data['id']}")

        return response.status_code == 201
    except Exception as e:
        print(f"❌ 创建场景资产失败: {e}")
        return False


def test_filter_assets():
    """测试过滤资产"""
    print_section("测试过滤资产")

    try:
        # 测试按项目 ID 和资产类型过滤
        response = requests.get(
            f"{API_BASE}/assets",
            params={
                "project_id": project_id,
                "asset_type": "character"
            }
        )

        data = print_response(response, "过滤资产（角色）响应")

        if response.status_code == 200 and data:
            print(f"\n✅ 角色资产数: {data['total']}")
            for asset in data['items']:
                print(f"   • {asset['name']}")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 过滤资产失败: {e}")
        return False


def test_update_asset():
    """测试更新资产"""
    print_section("测试更新资产")

    try:
        # 先获取第一个资产的 ID
        response = requests.get(
            f"{API_BASE}/assets",
            params={"project_id": project_id, "limit": 1}
        )

        if response.status_code != 200:
            print("❌ 获取资产列表失败，无法更新")
            return False

        data = response.json()
        if not data['items']:
            print("❌ 没有可更新的资产")
            return False

        asset_id = data['items'][0]['id']

        payload = {
            "description": "更新后的资产描述",
            "prompts": {
                "portrait": "更新的肖像提示词...",
                "full_body": "更新的全身像提示词..."
            }
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.put(
            f"{API_BASE}/assets/{asset_id}",
            json=payload
        )

        data = print_response(response, "更新资产响应")

        if response.status_code == 200:
            print(f"\n✅ 资产更新成功")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 更新资产失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 80)
    print("🚀 Universal Story Board - Step 4-B API 测试脚本")
    print("=" * 80)

    results = []

    # 0. 创建测试项目
    print("\n0️⃣ 准备工作：创建测试项目")
    results.append(("创建测试项目", test_create_test_project()))

    if not project_id:
        print("\n❌ 无法创建测试项目，终止测试")
        return 1

    # 1. 章节管理接口
    results.append(("获取章节列表", test_list_chapters()))
    results.append(("创建章节", test_create_chapter()))
    results.append(("批量创建章节", test_batch_create_chapters()))
    results.append(("更新章节", test_update_chapter()))

    # 2. 资产管理接口
    results.append(("获取资产列表", test_list_assets()))
    results.append(("创建角色资产", test_create_character_asset()))
    results.append(("创建场景资产", test_create_scene_asset()))
    results.append(("过滤资产", test_filter_assets()))
    results.append(("更新资产", test_update_asset()))

    # 3. 测试结果汇总
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)

    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:30s} {status}")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print(f"\n总计: {passed}/{total} 通过 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)

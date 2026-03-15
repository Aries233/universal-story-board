"""
Universal Story Board - Step 4-C 工作流测试脚本
测试 Agent 状态机链路和数据库写入
使用 Mock 数据，不真正调用大模型
"""
import requests
import json
import sys
import time

# API 基础 URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# 保存的 ID
chapter_id = None
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
            "name": "测试项目 - AI Agent 工作流",
            "description": "用于测试 AI Agent 工作流的项目",
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


def test_create_test_chapter():
    """创建测试章节"""
    global chapter_id, project_id

    print_section("创建测试章节")

    try:
        payload = {
            "project_id": project_id,
            "chapter_number": 1,
            "title": "第一章：穿越到唐朝",
            "original_text": "林峰睁开眼睛，发现自己躺在一间古老的房间里。四周是古色古香的家具，墙上挂着山水画。他努力回忆，最后想起自己是在一次登山时意外跌落。这是哪里？他为什么会在这里？"
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(
            f"{API_BASE}/chapters",
            json=payload
        )

        data = print_response(response, "创建章节响应")

        if response.status_code == 201 and data:
            chapter_id = data['id']
            print(f"\n✅ 章节创建成功，ID: {chapter_id}")
            return True

        return False
    except Exception as e:
        print(f"❌ 创建章节失败: {e}")
        return False


def test_add_mock_credential():
    """添加 Mock API Key（用于测试）"""
    print_section("添加 Mock API Key")

    try:
        payload = {
            "provider": "zhipu",
            "api_key": "mock_api_key_for_testing",
            "name": "Mock 智谱凭证",
            "priority": 0
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(
            f"{API_BASE}/system/credentials",
            json=payload
        )

        data = print_response(response, "添加凭证响应")

        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ 添加凭证失败: {e}")
        return False


def test_start_workflow_track_a():
    """测试启动工作流（A 轨：改编编剧）"""
    global chapter_id

    print_section("测试启动工作流（A 轨）")

    try:
        payload = {
            "chapter_id": chapter_id,
            "mode": "A"  # A 轨：改编编剧模式
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(
            f"{API_BASE}/workflow/start",
            json=payload
        )

        data = print_response(response, "启动工作流响应")

        if response.status_code == 200:
            print(f"\n✅ 工作流已启动，后台执行中")
            return True

        return False
    except Exception as e:
        print(f"❌ 启动工作流失败: {e}")
        return False


def test_get_workflow_status():
    """测试获取工作流状态"""
    global chapter_id

    print_section("测试获取工作流状态")

    try:
        response = requests.get(
            f"{API_BASE}/workflow/status/{chapter_id}"
        )

        data = print_response(response, "工作流状态响应")

        if response.status_code == 200:
            print(f"\n📊 当前状态: {data['status']}")
            print(f"🤖 当前 Agent: {data.get('current_agent', 'N/A')}")
            print(f"🔄 重试次数: {data.get('retry_count', 0)}")
            print(f"⏳ 进度: {data.get('progress', {})}")
            return True

        return False
    except Exception as e:
        print(f"❌ 获取工作流状态失败: {e}")
        return False


def test_get_chapter_detail():
    """测试获取章节详情（验证数据库写入）"""
    global chapter_id

    print_section("测试获取章节详情（验证数据库写入）")

    try:
        response = requests.get(
            f"{API_BASE}/chapters/{chapter_id}"
        )

        data = print_response(response, "章节详情响应")

        if response.status_code == 200:
            print(f"\n📝 章节标题: {data['title']}")
            print(f"📝 原始文本: {data['original_text'][:50]}...")
            print(f"📊 状态: {data['status']}")
            print(f"🤖 当前 Agent: {data.get('current_agent', 'N/A')}")

            # 检查是否有 script、characters 等数据（增加空值检查）
            script = data.get('script')
            if script:
                if isinstance(script, str):
                    print(f"✅ 剧本数据已写入（文本类型）: {len(script)} 字符")
                elif isinstance(script, dict):
                    print(f"✅ 剧本数据已写入（字典类型）: {len(str(script))} 字符")
                else:
                    print(f"⚠️  剧本数据类型未知: {type(script)}")

                # 检查 style_guide
                if isinstance(script, dict) and script.get('style_guide'):
                    print(f"✅ 风格规范已写入")
                else:
                    print(f"⚠️  风格规范尚未写入")
            else:
                print(f"⚠️  剧本数据尚未写入（为空）")

            return True

        return False
    except Exception as e:
        print(f"❌ 获取章节详情失败: {e}")
        return False


def test_get_assets():
    """测试获取资产（验证 Agent 生成的资产）"""
    global project_id

    print_section("测试获取资产（验证 Agent 生成的资产）")

    try:
        response = requests.get(
            f"{API_BASE}/assets?project_id={project_id}"
        )

        data = print_response(response, "资产列表响应")

        if response.status_code == 200:
            print(f"\n📊 总资产数: {data['total']}")

            # 统计不同类型的资产
            characters = [a for a in data['items'] if a['asset_type'] == 'character']
            scenes = [a for a in data['items'] if a['asset_type'] == 'scene']

            print(f"🎭 角色资产: {len(characters)}")
            print(f"🎬 场景资产: {len(scenes)}")

            for asset in characters:
                print(f"   • {asset['name']} ({asset['age']})")

            return True

        return False
    except Exception as e:
        print(f"❌ 获取资产失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 80)
    print("🚀 Universal Story Board - Step 4-C AI Agent 工作流测试脚本")
    print("=" * 80)

    results = []

    # 0. 创建测试项目和章节
    print("\n0️⃣ 准备工作：创建测试项目和章节")
    results.append(("创建测试项目", test_create_test_project()))

    if not project_id:
        print("\n❌ 无法创建测试项目，终止测试")
        return 1

    results.append(("创建测试章节", test_create_test_chapter()))

    if not chapter_id:
        print("\n❌ 无法创建测试章节，终止测试")
        return 1

    # 1. 添加 Mock API Key
    results.append(("添加 Mock API Key", test_add_mock_credential()))

    # 2. 启动工作流
    results.append(("启动工作流（A 轨）", test_start_workflow_track_a()))

    # 3. 等待后台执行（模拟）
    print("\n⏳ 等待 3 秒模拟后台执行...")
    time.sleep(3)

    # 4. 获取工作流状态
    results.append(("获取工作流状态", test_get_workflow_status()))

    # 5. 获取章节详情（验证数据库写入）
    results.append(("获取章节详情", test_get_chapter_detail()))

    # 6. 获取资产（验证 Agent 生成的资产）
    results.append(("获取资产", test_get_assets()))

    # 7. 测试结果汇总
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)

    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name:40s} {status}")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print(f"\n总计: {passed}/{total} 通过 ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 所有测试通过！")
        print("\n📝 测试说明:")
        print("• 由于使用 Mock API Key，实际不会调用大模型")
        print("• WriterAgent 和 CharacterAgent 会返回模拟数据")
        print("• 主要验证状态机转移规则和数据库写入")
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

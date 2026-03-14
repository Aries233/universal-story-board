"""
Universal Story Board - API 测试脚本
测试系统配置和项目管理的 API 接口
"""
import requests
import json
import sys

# API 基础 URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


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


def test_health_check():
    """测试健康检查接口"""
    print_section("测试健康检查接口")

    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "健康检查响应")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


def test_get_route_configs():
    """测试获取路由配置"""
    print_section("测试获取路由配置")

    try:
        response = requests.get(f"{API_BASE}/system/route-configs")
        data = print_response(response, "路由配置列表")

        if response.status_code == 200 and data:
            print(f"\n✅ 获取到 {len(data)} 条路由配置")
            for config in data:
                print(f"   • {config['model_type']}: {config['primary_model']}")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 获取路由配置失败: {e}")
        return False


def test_get_system_config():
    """测试获取系统配置"""
    print_section("测试获取系统配置")

    try:
        response = requests.get(f"{API_BASE}/system/config")
        data = print_response(response, "系统配置")

        if response.status_code == 200 and data:
            print(f"\n✅ 路由配置数: {len(data['route_configs'])}")
            print(f"✅ 凭证数: {len(data['credentials'])}")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 获取系统配置失败: {e}")
        return False


def test_create_project():
    """测试创建项目"""
    print_section("测试创建项目")

    try:
        payload = {
            "name": "测试项目",
            "description": "这是一个测试项目",
            "workflow_mode": "A"
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.post(
            f"{API_BASE}/projects",
            json=payload
        )

        data = print_response(response, "创建项目响应")

        if response.status_code == 201 and data:
            print(f"\n✅ 项目创建成功，ID: {data['id']}")
            return data['id']

        return None
    except Exception as e:
        print(f"❌ 创建项目失败: {e}")
        return None


def test_list_projects():
    """测试获取项目列表"""
    print_section("测试获取项目列表")

    try:
        response = requests.get(f"{API_BASE}/projects")
        data = print_response(response, "项目列表")

        if response.status_code == 200 and data:
            print(f"\n✅ 总项目数: {data['total']}")
            for project in data['items']:
                print(f"   • {project['name']} ({project['id']})")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 获取项目列表失败: {e}")
        return False


def test_get_project(project_id):
    """测试获取项目详情"""
    print_section(f"测试获取项目详情 (ID: {project_id})")

    try:
        response = requests.get(f"{API_BASE}/projects/{project_id}")
        data = print_response(response, "项目详情")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 获取项目详情失败: {e}")
        return False


def test_update_project(project_id):
    """测试更新项目"""
    print_section(f"测试更新项目 (ID: {project_id})")

    try:
        payload = {
            "description": "更新后的描述",
            "workflow_mode": "B"
        }

        print(f"\n📝 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")

        response = requests.put(
            f"{API_BASE}/projects/{project_id}",
            json=payload
        )

        data = print_response(response, "更新项目响应")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 更新项目失败: {e}")
        return False


def test_delete_project(project_id):
    """测试删除项目"""
    print_section(f"测试删除项目 (ID: {project_id})")

    try:
        response = requests.delete(f"{API_BASE}/projects/{project_id}")
        data = print_response(response, "删除项目响应")

        return response.status_code == 200
    except Exception as e:
        print(f"❌ 删除项目失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 80)
    print("🚀 Universal Story Board - API 测试脚本")
    print("=" * 80)

    results = []

    # 1. 健康检查
    results.append(("健康检查", test_health_check()))

    # 2. 系统配置接口
    results.append(("获取路由配置", test_get_route_configs()))
    results.append(("获取系统配置", test_get_system_config()))

    # 3. 项目管理接口
    project_id = test_create_project()

    if project_id:
        results.append(("创建项目", True))

        results.append(("获取项目列表", test_list_projects()))
        results.append(("获取项目详情", test_get_project(project_id)))
        results.append(("更新项目", test_update_project(project_id)))
        results.append(("删除项目", test_delete_project(project_id)))
    else:
        results.append(("创建项目", False))
        print("\n⚠️  项目创建失败，跳过后续测试")

    # 4. 测试结果汇总
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

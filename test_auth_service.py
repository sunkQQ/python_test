#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP Basic Auth 服务测试脚本
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def print_response(title, response):
    """
    格式化输出响应
    
    :param title: 标题
    :param response: 响应对象
    """
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    print(f"状态码: {response.status_code}")
    try:
        print(f"响应内容:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"响应内容:\n{response.text}")

def test_public_endpoint():
    """测试公开接口"""
    print("\n📌 测试1: 访问公开接口（无需认证）")
    response = requests.get(f"{BASE_URL}/public")
    print_response("公开接口测试", response)

def test_without_auth():
    """测试不提供认证访问受保护接口"""
    print("\n📌 测试2: 不提供认证访问受保护接口")
    response = requests.get(f"{BASE_URL}/protected")
    print_response("无认证访问受保护接口", response)

def test_with_invalid_auth():
    """测试使用错误的认证信息"""
    print("\n📌 测试3: 使用错误的用户名/密码")
    response = requests.get(
        f"{BASE_URL}/protected",
        auth=("wrong", "wrong")
    )
    print_response("错误认证信息", response)

def test_with_user_auth():
    """测试使用普通用户认证"""
    print("\n📌 测试4: 使用普通用户认证")
    response = requests.get(
        f"{BASE_URL}/protected",
        auth=("user", "user123")
    )
    print_response("普通用户认证", response)

def test_with_admin_auth():
    """测试使用管理员认证"""
    print("\n📌 测试5: 使用管理员认证")
    response = requests.get(
        f"{BASE_URL}/protected",
        auth=("admin", "admin123")
    )
    print_response("管理员认证", response)

def test_post_with_auth():
    """测试带认证的POST请求"""
    print("\n📌 测试6: POST请求（带认证）")
    data = {
        "name": "张三",
        "age": 25,
        "email": "zhangsan@example.com"
    }
    response = requests.post(
        f"{BASE_URL}/protected",
        auth=("admin", "admin123"),
        json=data
    )
    print_response("POST请求测试", response)

def test_user_info():
    """测试获取用户信息"""
    print("\n📌 测试7: 获取用户信息")
    response = requests.get(
        f"{BASE_URL}/user/info",
        auth=("admin", "admin123")
    )
    print_response("用户信息接口", response)

def test_system_status():
    """测试系统状态接口"""
    print("\n📌 测试8: 系统状态接口")
    response = requests.get(
        f"{BASE_URL}/status",
        auth=("user", "user123")
    )
    print_response("系统状态接口", response)

if __name__ == "__main__":
    print("=" * 60)
    print("  HTTP Basic Auth 服务测试")
    print("=" * 60)
    print("\n请确保服务已启动：python http_auth_service.py")
    print("\n测试账户:")
    print("  用户名: admin, 密码: admin123")
    print("  用户名: user, 密码: user123")
    
    # 执行所有测试
    input("\n按回车键开始测试...")
    
    try:
        test_public_endpoint()
        test_without_auth()
        test_with_invalid_auth()
        test_with_user_auth()
        test_with_admin_auth()
        test_post_with_auth()
        test_user_info()
        test_system_status()
        
        print("\n" + "=" * 60)
        print("  测试完成！")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务，请确保服务已启动！")
        print("  运行命令: python http_auth_service.py")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")

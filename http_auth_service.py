#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP Basic Auth 服务接口
使用 Flask 框架
"""

from flask import Flask, request, jsonify
from functools import wraps
import secrets

app = Flask(__name__)

# 配置用户名和密码（实际项目中应该从数据库或配置文件读取）
AUTH_USERS = {
    "admin": "admin123",  # 管理员用户
    "user": "user123"     # 普通用户
}

def check_auth(username, password):
    """
    检查用户名和密码是否正确
    
    :param username: 用户名
    :param password: 密码
    :return: 是否认证成功
    """
    # 检查用户名是否存在
    if username not in AUTH_USERS:
        return False
    # 检查密码是否匹配
    return secrets.compare_digest(AUTH_USERS[username], password)

def requires_auth(f):
    """
    装饰器：要求用户登录
    
    :param f: 被装饰的函数
    :return: 包装后的函数
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # 获取 Authorization 头
        auth = request.authorization
        
        # 如果没有提供认证信息
        if not auth:
            return jsonify({
                "success": False,
                "error": "Unauthorized",
                "message": "请提供用户名和密码"
            }), 401, {
                "WWW-Authenticate": 'Basic realm="Login Required"'
            }
        
        # 检查用户名和密码
        if not check_auth(auth.username, auth.password):
            return jsonify({
                "success": False,
                "error": "Forbidden",
                "message": "用户名或密码错误"
            }), 403
        
        # 认证成功，继续执行请求
        return f(*args, **kwargs)
    
    return decorated

@app.route("/", methods=["GET"])
def index():
    """
    首页（无需认证）
    """
    return jsonify({
        "success": True,
        "message": "欢迎使用HTTP Basic Auth服务",
        "endpoints": {
            "public": "/public",
            "protected": "/protected",
            "user_info": "/user/info",
            "status": "/status"
        }
    })

@app.route("/public", methods=["GET"])
def public_endpoint():
    """
    公开接口（无需认证）
    """
    return jsonify({
        "success": True,
        "message": "这是一个公开接口，任何人都可以访问",
        "data": {
            "public_info": "这里是公开信息",
            "timestamp": "2026-05-09"
        }
    })

@app.route("/protected", methods=["GET", "POST"])
@requires_auth
def protected_endpoint():
    """
    受保护接口（需要认证）
    """
    if request.method == "GET":
        return jsonify({
            "success": True,
            "message": "这是一个受保护的接口",
            "user": request.authorization.username,
            "data": {
                "protected_info": "这里是受保护的信息",
                "auth_type": "BasicAuth"
            }
        })
    elif request.method == "POST":
        # 获取请求数据
        data = request.get_json(force=True, silent=True) or {}
        
        return jsonify({
            "success": True,
            "message": "POST请求成功",
            "user": request.authorization.username,
            "received_data": data
        })

@app.route("/user/info", methods=["GET"])
@requires_auth
def user_info():
    """
    获取当前用户信息（需要认证）
    """
    username = request.authorization.username
    role = "admin" if username == "admin" else "user"
    
    return jsonify({
        "success": True,
        "data": {
            "username": username,
            "role": role,
            "permissions": {
                "read": True,
                "write": role == "admin",
                "delete": role == "admin"
            }
        }
    })

@app.route("/status", methods=["GET"])
@requires_auth
def system_status():
    """
    系统状态接口（需要认证）
    """
    return jsonify({
        "success": True,
        "data": {
            "status": "running",
            "uptime": "24h",
            "load": "low",
            "version": "1.0.0"
        }
    })

@app.errorhandler(404)
def not_found(error):
    """
    404 错误处理
    """
    return jsonify({
        "success": False,
        "error": "Not Found",
        "message": "请求的接口不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """
    500 错误处理
    """
    return jsonify({
        "success": False,
        "error": "Internal Server Error",
        "message": "服务器内部错误"
    }), 500

if __name__ == "__main__":
    print("=" * 50)
    print("HTTP Basic Auth 服务已启动")
    print("=" * 50)
    print("服务地址: http://127.0.0.1:5000")
    print("\n测试账户:")
    print("  用户名: admin, 密码: admin123")
    print("  用户名: user, 密码: user123")
    print("=" * 50)
    
    # 启动服务
    app.run(
        host="0.0.0.0",  # 监听所有网络接口
        port=5000,       # 端口
        debug=False      # 生产环境建议关闭debug
    )

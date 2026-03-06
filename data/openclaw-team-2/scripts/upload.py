#!/usr/bin/env python3
"""
文件上传模块
"""

import os
import hashlib
import base64
from datetime import datetime
from flask import jsonify
from cryptography.fernet import Fernet


def generate_key(password: str) -> bytes:
    """从密码生成 Fernet 密钥"""
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())


def register_upload_routes(app, DATA_DIR, CREDENTIAL_FILE, LOCAL_IP, PORT):
    """注册文件上传路由"""
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """文件上传 API - 需要登录"""
        from flask import request
        import hashlib
        import base64
        
        # 获取用户名和密码
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return jsonify({"error": "需要登录才能上传文件"}), 401
        
        # 验证用户
        user_dir = os.path.join(DATA_DIR, username)
        cred_file = os.path.join(user_dir, CREDENTIAL_FILE)
        
        if not os.path.exists(cred_file):
            return jsonify({"error": "用户不存在"}), 401
        
        try:
            with open(cred_file, 'r') as f:
                encrypted = f.read()
            cipher = Fernet(generate_key(password))
            decrypted = cipher.decrypt(encrypted.encode())
            if not decrypted.decode().startswith("OPENCLAW_USER:" + username):
                return jsonify({"error": "验证失败"}), 401
        except Exception:
            return jsonify({"error": "验证失败"}), 401
        
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({"error": "没有文件"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "文件名不能为空"}), 400
        
        # 保存文件
        user_uploads_dir = os.path.join(user_dir, "uploads")
        os.makedirs(user_uploads_dir, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(user_uploads_dir, safe_filename)
        
        file.save(file_path)
        
        # 返回文件 URL
        file_url = f"http://{LOCAL_IP}:{PORT}/uploads/{username}/{safe_filename}"
        print(f"📎 {username} 上传了文件: {file.filename} -> {safe_filename}")
        
        return jsonify({
            "success": True,
            "filename": safe_filename,
            "url": file_url,
            "path": file_path
        })
    
    # 提供上传的文件访问
    @app.route('/uploads/<username>/<filename>')
    def serve_upload(username, filename):
        """提供用户上传的文件"""
        from flask import send_from_directory
        file_path = os.path.join(DATA_DIR, username, "uploads", filename)
        if os.path.exists(file_path):
            return send_from_directory(os.path.join(DATA_DIR, username, "uploads"), filename)
        return "File not found", 404
    
    print("✅ 文件上传路由已注册")
    return app

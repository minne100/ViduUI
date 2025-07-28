#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vidu API UI 配置文件
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 基础配置
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
TEMP_DIR = BASE_DIR / "temp"

# API配置
API_KEY = ""  # 从.env文件或环境变量中读取

# 服务器配置
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 7860
SHARE_PUBLIC = False  # 是否生成公网链接

# UI配置
UI_TITLE = "🎬 Vidu API 客户端"
UI_DESCRIPTION = "一个功能完整的Vidu API客户端，支持视频生成、音频生成、任务管理和文件下载"
UI_THEME = "soft"  # 可选: "default", "soft", "glass", "monochrome"

# 文件上传配置
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/avi", "video/mov", "video/wmv"]
ALLOWED_AUDIO_TYPES = ["audio/mp3", "audio/wav", "audio/m4a", "audio/aac"]

# 任务配置
DEFAULT_TIMEOUT = 300  # 默认等待超时时间（秒）
MAX_TIMEOUT = 1800     # 最大等待超时时间（秒）
CHECK_INTERVAL = 3     # 任务状态检查间隔（秒）

# 下载配置
DEFAULT_FILENAME_PREFIX = "vidu_creation"
CHUNK_SIZE = 8192      # 下载块大小

# 模型配置
MODEL_DURATION_LIMITS = {
    "viduq1": [5],
    "viduq1-classic": [5], 
    "vidu2.0": [4],
    "vidu1.5": [4, 8]
}

# 创建必要的目录
def create_directories():
    """创建必要的目录"""
    directories = [DOWNLOAD_DIR, TEMP_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# 验证配置
def validate_config():
    """验证配置的有效性"""
    errors = []
    
    # 检查端口范围
    if not (1024 <= SERVER_PORT <= 65535):
        errors.append(f"服务器端口 {SERVER_PORT} 不在有效范围内 (1024-65535)")
    
    # 检查超时时间
    if DEFAULT_TIMEOUT > MAX_TIMEOUT:
        errors.append(f"默认超时时间 {DEFAULT_TIMEOUT} 不能大于最大超时时间 {MAX_TIMEOUT}")
    
    # 检查文件大小限制
    if MAX_FILE_SIZE <= 0:
        errors.append("最大文件大小必须大于0")
    
    return errors

# 加载.env文件
def load_env_file():
    """加载.env文件"""
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 已加载.env文件: {env_path}")
    else:
        print(f"⚠️  未找到.env文件: {env_path}")
        print("请复制 env_example.txt 为 .env 并设置您的API密钥")

# 获取环境变量配置
def get_env_config():
    """从环境变量获取配置"""
    global SERVER_PORT, SHARE_PUBLIC, DEFAULT_TIMEOUT, API_KEY
    
    # 服务器端口
    env_port = os.getenv("VIDU_SERVER_PORT")
    if env_port:
        try:
            SERVER_PORT = int(env_port)
        except ValueError:
            print(f"警告: 无效的环境变量 VIDU_SERVER_PORT: {env_port}")
    
    # 是否分享公网
    env_share = os.getenv("VIDU_SHARE_PUBLIC")
    if env_share:
        SHARE_PUBLIC = env_share.lower() in ["true", "1", "yes"]
    
    # 默认超时时间
    env_timeout = os.getenv("VIDU_DEFAULT_TIMEOUT")
    if env_timeout:
        try:
            DEFAULT_TIMEOUT = int(env_timeout)
        except ValueError:
            print(f"警告: 无效的环境变量 VIDU_DEFAULT_TIMEOUT: {env_timeout}")
    
    # API密钥
    env_api_key = os.getenv("VIDU_API_KEY")
    if env_api_key:
        API_KEY = env_api_key

# 初始化配置
def init_config():
    """初始化配置"""
    load_env_file()
    get_env_config()
    create_directories()
    
    errors = validate_config()
    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ 配置验证通过")
    return True

# 配置信息
CONFIG_INFO = {
    "base_dir": str(BASE_DIR),
    "download_dir": str(DOWNLOAD_DIR),
    "temp_dir": str(TEMP_DIR),
    "server_host": SERVER_HOST,
    "server_port": SERVER_PORT,
    "share_public": SHARE_PUBLIC,
    "ui_title": UI_TITLE,
    "ui_description": UI_DESCRIPTION,
    "ui_theme": UI_THEME,
    "max_file_size": MAX_FILE_SIZE,
    "default_timeout": DEFAULT_TIMEOUT,
    "max_timeout": MAX_TIMEOUT,
    "check_interval": CHECK_INTERVAL,
    "chunk_size": CHUNK_SIZE,
    "model_duration_limits": MODEL_DURATION_LIMITS,
    "api_key_configured": bool(API_KEY)
}

if __name__ == "__main__":
    # 测试配置
    if init_config():
        print("📋 配置信息:")
        for key, value in CONFIG_INFO.items():
            print(f"  {key}: {value}")
    else:
        print("❌ 配置初始化失败") 
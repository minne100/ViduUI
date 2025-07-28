#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件上传工具模块
处理文件上传、URL生成和文件清理
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple
import gradio as gr
from config import DOMAIN, BASE_DIR

# 上传文件存储目录
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 文件类型映射
FILE_TYPE_MAPPING = {
    "video": ["mp4", "mov", "avi", "wmv"],
    "audio": ["mp3", "wav", "m4a", "aac", "ogg", "wma"]
}

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return Path(filename).suffix.lower().lstrip('.')

def is_valid_file_type(file_path: str, allowed_types: list) -> bool:
    """检查文件类型是否有效"""
    if not file_path:
        return False
    
    ext = get_file_extension(file_path)
    return ext in allowed_types

def save_uploaded_file(file: gr.File, file_type: str) -> Optional[Tuple[str, str]]:
    """
    保存上传的文件
    
    Args:
        file: Gradio文件对象
        file_type: 文件类型 ("video" 或 "audio")
    
    Returns:
        Tuple[文件路径, 文件URL] 或 None
    """
    if not file or not file.name:
        return None
    
    # 检查文件类型
    if not is_valid_file_type(file.name, FILE_TYPE_MAPPING.get(file_type, [])):
        return None
    
    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        ext = get_file_extension(file.name)
        new_filename = f"{file_type}_{file_id}.{ext}"
        
        # 创建目标路径
        target_path = UPLOAD_DIR / new_filename
        
        # 复制文件
        shutil.copy2(file.name, target_path)
        
        # 生成URL
        file_url = f"http://{DOMAIN}/uploads/{new_filename}"
        
        return str(target_path), file_url
        
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return None

def cleanup_file(file_path: str) -> bool:
    """
    清理上传的文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        是否成功删除
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        print(f"❌ 删除文件失败: {e}")
    
    return False

def cleanup_files(file_paths: list) -> None:
    """
    批量清理文件
    
    Args:
        file_paths: 文件路径列表
    """
    for file_path in file_paths:
        if file_path:
            cleanup_file(file_path)

def get_upload_dir_size() -> int:
    """获取上传目录大小（字节）"""
    total_size = 0
    try:
        for file_path in UPLOAD_DIR.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    except Exception as e:
        print(f"❌ 计算目录大小失败: {e}")
    
    return total_size

def cleanup_old_files(max_size_mb: int = 100) -> None:
    """
    清理旧文件，保持目录大小在限制内
    
    Args:
        max_size_mb: 最大目录大小（MB）
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    current_size = get_upload_dir_size()
    
    if current_size <= max_size_bytes:
        return
    
    try:
        # 获取所有文件及其修改时间
        files = []
        for file_path in UPLOAD_DIR.rglob('*'):
            if file_path.is_file():
                mtime = file_path.stat().st_mtime
                files.append((file_path, mtime))
        
        # 按修改时间排序（最旧的在前）
        files.sort(key=lambda x: x[1])
        
        # 删除最旧的文件直到目录大小符合要求
        for file_path, _ in files:
            if get_upload_dir_size() <= max_size_bytes:
                break
            
            cleanup_file(str(file_path))
            
    except Exception as e:
        print(f"❌ 清理旧文件失败: {e}") 
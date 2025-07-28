#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vidu API UI 启动脚本
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from vidu_ui import create_ui
    import gradio as gr
    
    # 导入配置（配置已在模块导入时自动初始化）
    from config import SERVER_HOST, SERVER_PORT, SHARE_PUBLIC
    
    # 创建UI
    demo = create_ui()
    
    # 启动服务
    print("🚀 启动Web服务...")
    print(f"📱 本地访问地址: http://localhost:{SERVER_PORT}")
    print("🌐 公网访问地址: 启动后显示")
    print("⏹️  按 Ctrl+C 停止服务")
    
    # 配置静态文件服务
    from pathlib import Path
    uploads_dir = Path(__file__).parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    demo.launch(
        server_name=SERVER_HOST,
        server_port=SERVER_PORT,
        share=SHARE_PUBLIC,  # 使用配置文件中的设置
        show_error=True,
        quiet=False,
        # 配置静态文件服务
        app_kwargs={
            "static_dirs": {
                "/uploads": str(uploads_dir)
            }
        }
    )
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc() 
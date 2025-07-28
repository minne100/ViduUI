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
    
    print("🎬 启动 Vidu API 客户端 UI...")
    print("📁 当前目录:", current_dir)
    print("🔧 Gradio 版本:", gr.__version__)
    
    # 创建UI
    demo = create_ui()
    
    # 启动服务
    print("🚀 启动Web服务...")
    print("📱 本地访问地址: http://localhost:7860")
    print("🌐 公网访问地址: 启动后显示")
    print("⏹️  按 Ctrl+C 停止服务")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # 设置为True可以生成公网链接
        show_error=True,
        quiet=False
    )
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc() 
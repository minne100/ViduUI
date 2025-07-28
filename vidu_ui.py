#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vidu API Gradio UI界面
使用模块化设计，每个功能独立文件
"""

import gradio as gr
import os
from pathlib import Path

from vidu_client import ViduClient

# 导入功能模块
from image_to_video_module import create_image_to_video_ui
from reference_to_video_module import create_reference_to_video_ui
from start_end_to_video_module import create_start_end_to_video_ui
from text_to_video_module import create_text_to_video_ui
from upscale_pro_module import create_upscale_pro_ui
from lip_sync_module import create_lip_sync_ui
from text_to_audio_module import create_text_to_audio_ui
from timing_to_audio_module import create_timing_to_audio_ui

# 导入配置
try:
    from config import (
        UI_TITLE, UI_DESCRIPTION, UI_THEME, API_KEY
    )
except ImportError:
    # 如果配置文件不存在，使用默认值
    UI_TITLE = "🎬 Vidu API 客户端"
    UI_DESCRIPTION = "一个功能完整的Vidu API客户端，支持视频生成、音频生成和自动下载"
    UI_THEME = "soft"
    API_KEY = ""


class ViduUI:
    """Vidu API Gradio UI类"""
    
    def __init__(self):
        self.client = None
        
        # 初始化客户端
        if API_KEY:
            try:
                self.client = ViduClient(API_KEY)
                print(f"✅ 客户端初始化成功，API密钥已配置")
            except Exception as e:
                print(f"❌ 客户端初始化失败: {e}")
        else:
            print("⚠️  请在.env文件中设置VIDU_API_KEY")


def create_ui():
    """创建Gradio UI界面"""
    ui = ViduUI()
    
    with gr.Blocks(title=UI_TITLE, theme=UI_THEME) as demo:
        gr.Markdown(f"# {UI_TITLE}")
        gr.Markdown(UI_DESCRIPTION)
        
        # 显示API密钥状态
        if API_KEY:
            gr.Markdown("✅ API密钥已配置，可以开始使用")
            with gr.Tabs():
                # 只有在API密钥配置后才显示功能模块
                create_image_to_video_ui(ui.client)
                create_reference_to_video_ui(ui.client)
                create_start_end_to_video_ui(ui.client)
                create_text_to_video_ui(ui.client)
                create_upscale_pro_ui(ui.client)
                create_lip_sync_ui(ui.client)
                create_text_to_audio_ui(ui.client)
                create_timing_to_audio_ui(ui.client)
        else:
            gr.Markdown("⚠️  请在.env文件中设置VIDU_API_KEY")
            # 如果API密钥未配置，显示提示信息而不是功能模块
            gr.Markdown("""
            ## 🔧 配置说明
            
            1. 复制 `env_example.txt` 为 `.env`
            2. 在 `.env` 文件中设置您的 `VIDU_API_KEY`
            3. 重新启动应用程序
            
            ### 获取API密钥
            - 访问 [Vidu官网](https://vidu.com) 注册账号
            - 在控制台中获取API密钥
            - 将密钥添加到 `.env` 文件中
            """)
    
    return demo 
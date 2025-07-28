#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vidu API Gradio UI界面
提供完整的Vidu API功能，包括视频生成、音频生成和自动下载
"""

import gradio as gr
import os
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import tempfile
import shutil

from vidu_client import (
    ViduClient, ViduTask, ViduModel, ViduResolution, ViduAspectRatio,
    ViduMovementAmplitude, ViduTaskStatus, ViduAudioModel
)

# 导入配置
try:
    from config import (
        DOWNLOAD_DIR, TEMP_DIR, UI_TITLE, UI_DESCRIPTION, UI_THEME,
        DEFAULT_TIMEOUT, MAX_TIMEOUT, DEFAULT_FILENAME_PREFIX, CHUNK_SIZE,
        MODEL_DURATION_LIMITS, API_KEY, init_config
    )
except ImportError:
    # 如果配置文件不存在，使用默认值
    DOWNLOAD_DIR = Path("./downloads")
    TEMP_DIR = Path("./temp")
    UI_TITLE = "🎬 Vidu API 客户端"
    UI_DESCRIPTION = "一个功能完整的Vidu API客户端，支持视频生成、音频生成和自动下载"
    UI_THEME = "soft"
    DEFAULT_TIMEOUT = 300
    MAX_TIMEOUT = 1800
    DEFAULT_FILENAME_PREFIX = "vidu_creation"
    CHUNK_SIZE = 8192
    API_KEY = ""
    MODEL_DURATION_LIMITS = {
        "viduq1": [5],
        "viduq1-classic": [5], 
        "vidu2.0": [4],
        "vidu1.5": [4, 8]
    }
    
    def init_config():
        return True


class ViduUI:
    """Vidu API Gradio UI类"""
    
    def __init__(self):
        self.client = None
        self.download_dir = str(DOWNLOAD_DIR)
        
        # 初始化配置
        init_config()
        
        # 初始化客户端
        if API_KEY:
            try:
                self.client = ViduClient(API_KEY)
            except Exception as e:
                print(f"❌ 客户端初始化失败: {e}")
        else:
            print("⚠️  请在.env文件中设置VIDU_API_KEY")
        
        # 确保下载目录存在
        os.makedirs(self.download_dir, exist_ok=True)
    
    def create_image_to_video(self, model: str, image_files: List[str], prompt: str, 
                             duration: int, seed: int, resolution: str, 
                             movement_amplitude: str, bgm: bool) -> str:
        """创建图生视频任务并自动下载"""
        if not self.client:
            return "❌ 客户端未初始化，请在.env文件中设置VIDU_API_KEY"
        
        try:
            # 处理图片文件
            images = []
            for img_file in image_files:
                if img_file:
                    # 将Gradio文件转换为Base64
                    base64_img = ViduClient.encode_image_to_base64(img_file.name, "image/jpeg")
                    images.append(base64_img)
            
            if not images:
                return "❌ 请至少上传一张图片"
            
            # 创建任务
            response = self.client.image_to_video(
                model=model,
                images=images,
                prompt=prompt if prompt.strip() else None,
                duration=duration,
                seed=seed if seed != 0 else None,
                resolution=resolution if resolution != "auto" else None,
                movement_amplitude=movement_amplitude if movement_amplitude != "auto" else None,
                bgm=bgm
            )
            
            task_id = response['id']
            task = ViduTask(self.client, task_id)
            
            # 等待任务完成并自动下载
            result = f"✅ 图生视频任务创建成功！\n任务ID: {task_id}\n"
            result += "⏳ 正在等待任务完成...\n"
            
            try:
                # 等待任务完成
                task_info = task.wait_for_completion(timeout=DEFAULT_TIMEOUT)
                
                if task_info.get('state') == ViduTaskStatus.SUCCESS:
                    # 自动下载
                    filename_prefix = f"img2vid_{task_id}"
                    downloaded_files = task.download_creation(
                        save_dir=self.download_dir,
                        filename_prefix=filename_prefix
                    )
                    
                    result += "✅ 任务完成！文件已自动下载到:\n"
                    for file_type, file_path in downloaded_files.items():
                        result += f"  {file_type}: {file_path}\n"
                else:
                    result += f"❌ 任务失败: {task_info.get('err_code', '未知错误')}\n"
                    
            except Exception as e:
                result += f"❌ 等待任务完成失败: {str(e)}\n"
            
            return result
            
        except Exception as e:
            return f"❌ 创建任务失败: {str(e)}"
    
    def create_reference_to_video(self, model: str, image_files: List[str], prompt: str,
                                 duration: int, seed: int, aspect_ratio: str, resolution: str,
                                 movement_amplitude: str, bgm: bool) -> str:
        """创建参考生视频任务并自动下载"""
        if not self.client:
            return "❌ 客户端未初始化，请在.env文件中设置VIDU_API_KEY"
        
        try:
            # 处理图片文件
            images = []
            for img_file in image_files:
                if img_file:
                    # 将Gradio文件转换为Base64
                    base64_img = ViduClient.encode_image_to_base64(img_file.name, "image/jpeg")
                    images.append(base64_img)
            
            if not images:
                return "❌ 请至少上传一张参考图片"
            
            if not prompt.strip():
                return "❌ 请输入文本提示词"
            
            # 创建任务
            response = self.client.reference_to_video(
                model=model,
                images=images,
                prompt=prompt.strip(),
                duration=duration,
                seed=seed if seed != 0 else None,
                aspect_ratio=aspect_ratio if aspect_ratio != "auto" else None,
                resolution=resolution if resolution != "auto" else None,
                movement_amplitude=movement_amplitude if movement_amplitude != "auto" else None,
                bgm=bgm
            )
            
            task_id = response['id']
            task = ViduTask(self.client, task_id)
            
            # 等待任务完成并自动下载
            result = f"✅ 参考生视频任务创建成功！\n任务ID: {task_id}\n"
            result += "⏳ 正在等待任务完成...\n"
            
            try:
                # 等待任务完成
                task_info = task.wait_for_completion(timeout=DEFAULT_TIMEOUT)
                
                if task_info.get('state') == ViduTaskStatus.SUCCESS:
                    # 自动下载
                    filename_prefix = f"ref2vid_{task_id}"
                    downloaded_files = task.download_creation(
                        save_dir=self.download_dir,
                        filename_prefix=filename_prefix
                    )
                    
                    result += "✅ 任务完成！文件已自动下载到:\n"
                    for file_type, file_path in downloaded_files.items():
                        result += f"  {file_type}: {file_path}\n"
                else:
                    result += f"❌ 任务失败: {task_info.get('err_code', '未知错误')}\n"
                    
            except Exception as e:
                result += f"❌ 等待任务完成失败: {str(e)}\n"
            
            return result
            
        except Exception as e:
            return f"❌ 创建任务失败: {str(e)}"
    
    def create_start_end_to_video(self, model: str, start_image: str, end_image: str,
                                 prompt: str, duration: int, seed: int, resolution: str,
                                 movement_amplitude: str, bgm: bool) -> str:
        """创建首尾帧生视频任务并自动下载"""
        if not self.client:
            return "❌ 客户端未初始化，请在.env文件中设置VIDU_API_KEY"
        
        try:
            # 处理图片文件
            images = []
            if start_image:
                base64_img = ViduClient.encode_image_to_base64(start_image.name, "image/jpeg")
                images.append(base64_img)
            if end_image:
                base64_img = ViduClient.encode_image_to_base64(end_image.name, "image/jpeg")
                images.append(base64_img)
            
            if len(images) != 2:
                return "❌ 请上传首帧和尾帧两张图片"
            
            # 创建任务
            response = self.client.start_end_to_video(
                model=model,
                images=images,
                prompt=prompt if prompt.strip() else None,
                duration=duration,
                seed=seed if seed != 0 else None,
                resolution=resolution if resolution != "auto" else None,
                movement_amplitude=movement_amplitude if movement_amplitude != "auto" else None,
                bgm=bgm
            )
            
            task_id = response['id']
            task = ViduTask(self.client, task_id)
            
            # 等待任务完成并自动下载
            result = f"✅ 首尾帧生视频任务创建成功！\n任务ID: {task_id}\n"
            result += "⏳ 正在等待任务完成...\n"
            
            try:
                # 等待任务完成
                task_info = task.wait_for_completion(timeout=DEFAULT_TIMEOUT)
                
                if task_info.get('state') == ViduTaskStatus.SUCCESS:
                    # 自动下载
                    filename_prefix = f"startend_{task_id}"
                    downloaded_files = task.download_creation(
                        save_dir=self.download_dir,
                        filename_prefix=filename_prefix
                    )
                    
                    result += "✅ 任务完成！文件已自动下载到:\n"
                    for file_type, file_path in downloaded_files.items():
                        result += f"  {file_type}: {file_path}\n"
                else:
                    result += f"❌ 任务失败: {task_info.get('err_code', '未知错误')}\n"
                    
            except Exception as e:
                result += f"❌ 等待任务完成失败: {str(e)}\n"
            
            return result
            
        except Exception as e:
            return f"❌ 创建任务失败: {str(e)}"
    
    def create_text_to_video(self, model: str, prompt: str, duration: int, seed: int,
                            aspect_ratio: str, resolution: str, movement_amplitude: str, bgm: bool) -> str:
        """创建文生视频任务并自动下载"""
        if not self.client:
            return "❌ 客户端未初始化，请在.env文件中设置VIDU_API_KEY"
        
        try:
            if not prompt.strip():
                return "❌ 请输入文本提示词"
            
            # 创建任务
            response = self.client.text_to_video(
                model=model,
                prompt=prompt.strip(),
                duration=duration,
                seed=seed if seed != 0 else None,
                aspect_ratio=aspect_ratio if aspect_ratio != "auto" else None,
                resolution=resolution if resolution != "auto" else None,
                movement_amplitude=movement_amplitude if movement_amplitude != "auto" else None,
                bgm=bgm
            )
            
            task_id = response['id']
            task = ViduTask(self.client, task_id)
            
            # 等待任务完成并自动下载
            result = f"✅ 文生视频任务创建成功！\n任务ID: {task_id}\n"
            result += "⏳ 正在等待任务完成...\n"
            
            try:
                # 等待任务完成
                task_info = task.wait_for_completion(timeout=DEFAULT_TIMEOUT)
                
                if task_info.get('state') == ViduTaskStatus.SUCCESS:
                    # 自动下载
                    filename_prefix = f"text2vid_{task_id}"
                    downloaded_files = task.download_creation(
                        save_dir=self.download_dir,
                        filename_prefix=filename_prefix
                    )
                    
                    result += "✅ 任务完成！文件已自动下载到:\n"
                    for file_type, file_path in downloaded_files.items():
                        result += f"  {file_type}: {file_path}\n"
                else:
                    result += f"❌ 任务失败: {task_info.get('err_code', '未知错误')}\n"
                    
            except Exception as e:
                result += f"❌ 等待任务完成失败: {str(e)}\n"
            
            return result
            
        except Exception as e:
            return f"❌ 创建任务失败: {str(e)}"
    
    def create_upscale_pro(self, video_url: str) -> str:
        """创建智能超清任务并自动下载"""
        if not self.client:
            return "❌ 客户端未初始化，请在.env文件中设置VIDU_API_KEY"
        
        try:
            if not video_url.strip():
                return "❌ 请输入视频URL"
            
            response = self.client.upscale_pro(video_url=video_url.strip())
            task_id = response['id']
            task = ViduTask(self.client, task_id)
            
            # 等待任务完成并自动下载
            result = f"✅ 智能超清任务创建成功！\n任务ID: {task_id}\n"
            result += "⏳ 正在等待任务完成...\n"
            
            try:
                # 等待任务完成
                task_info = task.wait_for_completion(timeout=DEFAULT_TIMEOUT)
                
                if task_info.get('state') == ViduTaskStatus.SUCCESS:
                    # 自动下载
                    filename_prefix = f"upscale_{task_id}"
                    downloaded_files = task.download_creation(
                        save_dir=self.download_dir,
                        filename_prefix=filename_prefix
                    )
                    
                    result += "✅ 任务完成！文件已自动下载到:\n"
                    for file_type, file_path in downloaded_files.items():
                        result += f"  {file_type}: {file_path}\n"
                else:
                    result += f"❌ 任务失败: {task_info.get('err_code', '未知错误')}\n"
                    
            except Exception as e:
                result += f"❌ 等待任务完成失败: {str(e)}\n"
            
            return result
            
        except Exception as e:
            return f"❌ 创建任务失败: {str(e)}"
    
    def create_lip_sync(self, video_url: str, audio_url: str) -> str:
        """创建对口型任务并自动下载"""
        if not self.client:
            return "❌ 客户端未初始化，请在.env文件中设置VIDU_API_KEY"
        
        try:
            if not video_url.strip():
                return "❌ 请输入视频URL"
            if not audio_url.strip():
                return "❌ 请输入音频URL"
            
            response = self.client.lip_sync(
                video_url=video_url.strip(),
                audio_url=audio_url.strip()
            )
            task_id = response['id']
            task = ViduTask(self.client, task_id)
            
            # 等待任务完成并自动下载
            result = f"✅ 对口型任务创建成功！\n任务ID: {task_id}\n"
            result += "⏳ 正在等待任务完成...\n"
            
            try:
                # 等待任务完成
                task_info = task.wait_for_completion(timeout=DEFAULT_TIMEOUT)
                
                if task_info.get('state') == ViduTaskStatus.SUCCESS:
                    # 自动下载
                    filename_prefix = f"lipsync_{task_id}"
                    downloaded_files = task.download_creation(
                        save_dir=self.download_dir,
                        filename_prefix=filename_prefix
                    )
                    
                    result += "✅ 任务完成！文件已自动下载到:\n"
                    for file_type, file_path in downloaded_files.items():
                        result += f"  {file_type}: {file_path}\n"
                else:
                    result += f"❌ 任务失败: {task_info.get('err_code', '未知错误')}\n"
                    
            except Exception as e:
                result += f"❌ 等待任务完成失败: {str(e)}\n"
            
            return result
            
        except Exception as e:
            return f"❌ 创建任务失败: {str(e)}"
    
    def create_text_to_audio(self, model: str, text: str, voice_id: str) -> str:
        """创建文生音频任务并自动下载"""
        if not self.client:
            return "❌ 客户端未初始化，请在.env文件中设置VIDU_API_KEY"
        
        try:
            if not text.strip():
                return "❌ 请输入文本内容"
            
            response = self.client.text_to_audio(
                model=model,
                text=text.strip(),
                voice_id=voice_id if voice_id.strip() else None
            )
            task_id = response['id']
            task = ViduTask(self.client, task_id)
            
            # 等待任务完成并自动下载
            result = f"✅ 文生音频任务创建成功！\n任务ID: {task_id}\n"
            result += "⏳ 正在等待任务完成...\n"
            
            try:
                # 等待任务完成
                task_info = task.wait_for_completion(timeout=DEFAULT_TIMEOUT)
                
                if task_info.get('state') == ViduTaskStatus.SUCCESS:
                    # 自动下载
                    filename_prefix = f"text2audio_{task_id}"
                    downloaded_files = task.download_creation(
                        save_dir=self.download_dir,
                        filename_prefix=filename_prefix
                    )
                    
                    result += "✅ 任务完成！文件已自动下载到:\n"
                    for file_type, file_path in downloaded_files.items():
                        result += f"  {file_type}: {file_path}\n"
                else:
                    result += f"❌ 任务失败: {task_info.get('err_code', '未知错误')}\n"
                    
            except Exception as e:
                result += f"❌ 等待任务完成失败: {str(e)}\n"
            
            return result
            
        except Exception as e:
            return f"❌ 创建任务失败: {str(e)}"
    
    def create_timing_to_audio(self, model: str, text: str, timing_json: str, voice_id: str) -> str:
        """创建可控文生音效任务并自动下载"""
        if not self.client:
            return "❌ 客户端未初始化，请在.env文件中设置VIDU_API_KEY"
        
        try:
            if not text.strip():
                return "❌ 请输入文本内容"
            
            # 解析timing JSON
            timing = None
            if timing_json.strip():
                try:
                    timing = json.loads(timing_json)
                except json.JSONDecodeError:
                    return "❌ Timing JSON格式错误"
            
            response = self.client.timing_to_audio(
                model=model,
                text=text.strip(),
                timing=timing or [],
                voice_id=voice_id if voice_id.strip() else None
            )
            task_id = response['id']
            task = ViduTask(self.client, task_id)
            
            # 等待任务完成并自动下载
            result = f"✅ 可控文生音效任务创建成功！\n任务ID: {task_id}\n"
            result += "⏳ 正在等待任务完成...\n"
            
            try:
                # 等待任务完成
                task_info = task.wait_for_completion(timeout=DEFAULT_TIMEOUT)
                
                if task_info.get('state') == ViduTaskStatus.SUCCESS:
                    # 自动下载
                    filename_prefix = f"timing2audio_{task_id}"
                    downloaded_files = task.download_creation(
                        save_dir=self.download_dir,
                        filename_prefix=filename_prefix
                    )
                    
                    result += "✅ 任务完成！文件已自动下载到:\n"
                    for file_type, file_path in downloaded_files.items():
                        result += f"  {file_type}: {file_path}\n"
                else:
                    result += f"❌ 任务失败: {task_info.get('err_code', '未知错误')}\n"
                    
            except Exception as e:
                result += f"❌ 等待任务完成失败: {str(e)}\n"
            
            return result
            
        except Exception as e:
            return f"❌ 创建任务失败: {str(e)}"


def create_ui():
    """创建Gradio UI界面"""
    ui = ViduUI()
    
    with gr.Blocks(title=UI_TITLE, theme=UI_THEME) as demo:
        gr.Markdown(f"# {UI_TITLE}")
        gr.Markdown(UI_DESCRIPTION)
        
        # 显示API密钥状态
        if API_KEY:
            gr.Markdown("✅ API密钥已配置，可以开始使用")
        else:
            gr.Markdown("⚠️  请在.env文件中设置VIDU_API_KEY")
        
        with gr.Tabs():
            # 视频生成标签页
            with gr.Tab("🎥 视频生成"):
                with gr.Accordion("图生视频", open=True):
                    with gr.Row():
                        img2vid_model = gr.Dropdown(
                            choices=[str(m) for m in ViduModel],
                            value=str(ViduModel.VIDU1_5),
                            label="模型"
                        )
                        img2vid_images = gr.File(
                            file_count="multiple",
                            label="上传图片（支持1张）",
                            file_types=["image"]
                        )
                    
                    img2vid_prompt = gr.Textbox(
                        label="文本提示词（可选）",
                        placeholder="描述您想要的视频效果...",
                        lines=3
                    )
                    
                    with gr.Row():
                        img2vid_duration = gr.Slider(
                            minimum=4, maximum=8, step=1, value=4,
                            label="视频时长（秒）"
                        )
                        img2vid_seed = gr.Number(
                            value=0, label="随机种子（0表示随机）"
                        )
                    
                    with gr.Row():
                        img2vid_resolution = gr.Dropdown(
                            choices=["auto"] + [str(r) for r in ViduResolution],
                            value="auto",
                            label="分辨率"
                        )
                        img2vid_movement = gr.Dropdown(
                            choices=["auto"] + [str(m) for m in ViduMovementAmplitude],
                            value="auto",
                            label="运动幅度"
                        )
                        img2vid_bgm = gr.Checkbox(label="添加背景音乐", value=False)
                    
                    img2vid_btn = gr.Button("创建图生视频任务", variant="primary")
                    img2vid_output = gr.Textbox(label="任务结果", lines=5, interactive=False)
                    img2vid_btn.click(ui.create_image_to_video, 
                                    inputs=[img2vid_model, img2vid_images, img2vid_prompt,
                                           img2vid_duration, img2vid_seed, img2vid_resolution,
                                           img2vid_movement, img2vid_bgm], 
                                    outputs=[img2vid_output])
                
                with gr.Accordion("参考生视频", open=False):
                    with gr.Row():
                        ref2vid_model = gr.Dropdown(
                            choices=[str(m) for m in ViduModel],
                            value=str(ViduModel.VIDU1_5),
                            label="模型"
                        )
                        ref2vid_images = gr.File(
                            file_count="multiple",
                            label="上传参考图片（支持1-7张）",
                            file_types=["image"]
                        )
                    
                    ref2vid_prompt = gr.Textbox(
                        label="文本提示词（必填）",
                        placeholder="描述您想要的视频效果...",
                        lines=3
                    )
                    
                    with gr.Row():
                        ref2vid_duration = gr.Slider(
                            minimum=4, maximum=8, step=1, value=4,
                            label="视频时长（秒）"
                        )
                        ref2vid_seed = gr.Number(
                            value=0, label="随机种子（0表示随机）"
                        )
                    
                    with gr.Row():
                        ref2vid_aspect = gr.Dropdown(
                            choices=["auto"] + [str(a) for a in ViduAspectRatio],
                            value="auto",
                            label="宽高比"
                        )
                        ref2vid_resolution = gr.Dropdown(
                            choices=["auto"] + [str(r) for r in ViduResolution],
                            value="auto",
                            label="分辨率"
                        )
                        ref2vid_movement = gr.Dropdown(
                            choices=["auto"] + [str(m) for m in ViduMovementAmplitude],
                            value="auto",
                            label="运动幅度"
                        )
                        ref2vid_bgm = gr.Checkbox(label="添加背景音乐", value=False)
                    
                    ref2vid_btn = gr.Button("创建参考生视频任务", variant="primary")
                    ref2vid_output = gr.Textbox(label="任务结果", lines=5, interactive=False)
                    ref2vid_btn.click(ui.create_reference_to_video, 
                                    inputs=[ref2vid_model, ref2vid_images, ref2vid_prompt,
                                           ref2vid_duration, ref2vid_seed, ref2vid_aspect,
                                           ref2vid_resolution, ref2vid_movement, ref2vid_bgm], 
                                    outputs=[ref2vid_output])
                
                with gr.Accordion("首尾帧生视频", open=False):
                    with gr.Row():
                        startend_model = gr.Dropdown(
                            choices=[str(m) for m in ViduModel],
                            value=str(ViduModel.VIDU1_5),
                            label="模型"
                        )
                        startend_start = gr.File(
                            label="首帧图片",
                            file_types=["image"]
                        )
                        startend_end = gr.File(
                            label="尾帧图片",
                            file_types=["image"]
                        )
                    
                    startend_prompt = gr.Textbox(
                        label="文本提示词（可选）",
                        placeholder="描述您想要的视频效果...",
                        lines=3
                    )
                    
                    with gr.Row():
                        startend_duration = gr.Slider(
                            minimum=4, maximum=8, step=1, value=4,
                            label="视频时长（秒）"
                        )
                        startend_seed = gr.Number(
                            value=0, label="随机种子（0表示随机）"
                        )
                    
                    with gr.Row():
                        startend_resolution = gr.Dropdown(
                            choices=["auto"] + [str(r) for r in ViduResolution],
                            value="auto",
                            label="分辨率"
                        )
                        startend_movement = gr.Dropdown(
                            choices=["auto"] + [str(m) for m in ViduMovementAmplitude],
                            value="auto",
                            label="运动幅度"
                        )
                        startend_bgm = gr.Checkbox(label="添加背景音乐", value=False)
                    
                    startend_btn = gr.Button("创建首尾帧生视频任务", variant="primary")
                    startend_output = gr.Textbox(label="任务结果", lines=5, interactive=False)
                    startend_btn.click(ui.create_start_end_to_video, 
                                     inputs=[startend_model, startend_start, startend_end,
                                            startend_prompt, startend_duration, startend_seed,
                                            startend_resolution, startend_movement, startend_bgm], 
                                     outputs=[startend_output])
                
                with gr.Accordion("文生视频", open=False):
                    with gr.Row():
                        text2vid_model = gr.Dropdown(
                            choices=[str(m) for m in ViduModel],
                            value=str(ViduModel.VIDU1_5),
                            label="模型"
                        )
                    
                    text2vid_prompt = gr.Textbox(
                        label="文本提示词（必填）",
                        placeholder="描述您想要的视频效果...",
                        lines=5
                    )
                    
                    with gr.Row():
                        text2vid_duration = gr.Slider(
                            minimum=4, maximum=8, step=1, value=4,
                            label="视频时长（秒）"
                        )
                        text2vid_seed = gr.Number(
                            value=0, label="随机种子（0表示随机）"
                        )
                    
                    with gr.Row():
                        text2vid_aspect = gr.Dropdown(
                            choices=["auto"] + [str(a) for a in ViduAspectRatio],
                            value="auto",
                            label="宽高比"
                        )
                        text2vid_resolution = gr.Dropdown(
                            choices=["auto"] + [str(r) for r in ViduResolution],
                            value="auto",
                            label="分辨率"
                        )
                        text2vid_movement = gr.Dropdown(
                            choices=["auto"] + [str(m) for m in ViduMovementAmplitude],
                            value="auto",
                            label="运动幅度"
                        )
                        text2vid_bgm = gr.Checkbox(label="添加背景音乐", value=False)
                    
                    text2vid_btn = gr.Button("创建文生视频任务", variant="primary")
                    text2vid_output = gr.Textbox(label="任务结果", lines=5, interactive=False)
                    text2vid_btn.click(ui.create_text_to_video, 
                                     inputs=[text2vid_model, text2vid_prompt, text2vid_duration,
                                            text2vid_seed, text2vid_aspect, text2vid_resolution,
                                            text2vid_movement, text2vid_bgm], 
                                     outputs=[text2vid_output])
            
            # 视频处理标签页
            with gr.Tab("🎬 视频处理"):
                with gr.Accordion("智能超清", open=True):
                    upscale_video_url = gr.Textbox(
                        label="视频URL",
                        placeholder="请输入要超清的视频URL",
                        lines=2
                    )
                    upscale_btn = gr.Button("创建智能超清任务", variant="primary")
                    upscale_output = gr.Textbox(label="任务结果", lines=5, interactive=False)
                    upscale_btn.click(ui.create_upscale_pro, inputs=[upscale_video_url], outputs=[upscale_output])
                
                with gr.Accordion("对口型", open=False):
                    with gr.Row():
                        lip_video_url = gr.Textbox(
                            label="视频URL",
                            placeholder="请输入视频URL",
                            lines=2
                        )
                        lip_audio_url = gr.Textbox(
                            label="音频URL",
                            placeholder="请输入音频URL",
                            lines=2
                        )
                    lip_btn = gr.Button("创建对口型任务", variant="primary")
                    lip_output = gr.Textbox(label="任务结果", lines=5, interactive=False)
                    lip_btn.click(ui.create_lip_sync, inputs=[lip_video_url, lip_audio_url], outputs=[lip_output])
            
            # 音频生成标签页
            with gr.Tab("🎵 音频生成"):
                with gr.Accordion("文生音频", open=True):
                    with gr.Row():
                        text2audio_model = gr.Dropdown(
                            choices=[str(m) for m in ViduAudioModel],
                            value=str(ViduAudioModel.VIDU_AUDIO),
                            label="音频模型"
                        )
                    
                    text2audio_text = gr.Textbox(
                        label="文本内容",
                        placeholder="请输入要转换为音频的文本...",
                        lines=5
                    )
                    text2audio_voice_id = gr.Textbox(
                        label="声音ID（可选）",
                        placeholder="留空使用默认声音",
                        lines=1
                    )
                    
                    text2audio_btn = gr.Button("创建文生音频任务", variant="primary")
                    text2audio_output = gr.Textbox(label="任务结果", lines=5, interactive=False)
                    text2audio_btn.click(ui.create_text_to_audio, 
                                       inputs=[text2audio_model, text2audio_text, text2audio_voice_id], 
                                       outputs=[text2audio_output])
                
                with gr.Accordion("可控文生音效", open=False):
                    with gr.Row():
                        timing2audio_model = gr.Dropdown(
                            choices=[str(m) for m in ViduAudioModel],
                            value=str(ViduAudioModel.VIDU_AUDIO),
                            label="音频模型"
                        )
                    
                    timing2audio_text = gr.Textbox(
                        label="文本内容",
                        placeholder="请输入要转换为音频的文本...",
                        lines=3
                    )
                    timing2audio_timing = gr.Textbox(
                        label="时间控制参数（JSON格式）",
                        placeholder='[{"start_time": 0.0, "end_time": 2.0, "text": "欢迎"}]',
                        lines=5
                    )
                    timing2audio_voice_id = gr.Textbox(
                        label="声音ID（可选）",
                        placeholder="留空使用默认声音",
                        lines=1
                    )
                    
                    timing2audio_btn = gr.Button("创建可控文生音效任务", variant="primary")
                    timing2audio_output = gr.Textbox(label="任务结果", lines=5, interactive=False)
                    timing2audio_btn.click(ui.create_timing_to_audio, 
                                         inputs=[timing2audio_model, timing2audio_text, 
                                                timing2audio_timing, timing2audio_voice_id], 
                                         outputs=[timing2audio_output])
            
            # 帮助标签页
            with gr.Tab("📖 帮助"):
                gr.Markdown("""
                ## 使用说明
                
                ### 1. 配置API密钥
                - 复制 `env_example.txt` 为 `.env` 文件
                - 在 `.env` 文件中设置您的Vidu API密钥
                - 或者设置环境变量 `VIDU_API_KEY`
                
                ### 2. 创建任务
                - 选择相应的功能标签页（视频生成、视频处理、音频生成）
                - 填写必要的参数
                - 点击创建任务按钮
                - 系统会自动等待任务完成并下载文件
                
                ### 3. 自动下载
                - 任务完成后会自动下载生成的文件
                - 文件保存在 `./downloads` 目录中
                - 文件名包含任务ID和类型标识
                
                ### 4. 注意事项
                - 任务创建后会自动等待完成，请耐心等待
                - 下载的文件会保存在本地 `downloads` 目录
                - 支持多种视频和音频格式
                
                ### 5. 模型支持
                - **viduq1**: 支持5秒视频
                - **vidu2.0**: 支持4秒视频
                - **vidu1.5**: 支持4秒和8秒视频
                
                ### 6. 文件组织
                - 下载的文件按任务ID组织
                - 支持视频和封面图片下载
                - 自动创建目录结构
                """)
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch() 

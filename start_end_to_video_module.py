#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起止生视频功能模块
包含UI界面和业务逻辑
"""

import gradio as gr
import time
from typing import List
from vidu_client import ViduClient, ViduModel, ViduResolution, ViduAspectRatio, ViduTaskStatus
from utils import get_error_message, convert_movement_amplitude, update_duration_options


def get_start_end_resolution_options(model: str, duration: str) -> list:
    """根据模型和时长获取可用的分辨率选项（首尾帧生视频）"""
    resolution_map = {
        "viduq1": {
            "5": ["1080p"]  # viduq1 5秒：默认1080p，可选1080p
        },
        "viduq1-classic": {
            "5": ["1080p"]  # viduq1-classic 5秒：默认1080p，可选1080p
        },
        "vidu2.0": {
            "4": ["360p", "720p", "1080p"],  # vidu2.0 4秒：默认360p，可选360p、720p、1080p
            "8": ["720p"]  # vidu2.0 8秒：默认720p，可选720p
        },
        "vidu1.5": {
            "4": ["360p", "720p", "1080p"],  # vidu1.5 4秒：默认360p，可选360p、720p、1080p
            "8": ["720p"]  # vidu1.5 8秒：默认720p，可选720p
        }
    }
    
    return resolution_map.get(model, {}).get(duration, ["360p", "720p", "1080p"])

def get_start_end_default_resolution(model: str, duration: str) -> str:
    """根据模型和时长获取默认分辨率（首尾帧生视频）"""
    default_map = {
        "viduq1": {"5": "1080p"},
        "viduq1-classic": {"5": "1080p"},
        "vidu2.0": {"4": "360p", "8": "720p"},
        "vidu1.5": {"4": "360p", "8": "720p"}
    }
    
    return default_map.get(model, {}).get(duration, "360p")


def create_start_end_to_video_task(client: ViduClient, model: str, image_files: List[str], 
                                  prompt: str, duration: str, seed: int, resolution: str,
                                  movement_amplitude: str, bgm: str) -> str:
    """创建首尾帧生视频任务并轮询结果"""
    try:
        # 处理图片文件
        images = []
        for img_file in image_files:
            if img_file:
                base64_img = ViduClient.encode_image_to_base64(img_file.name, "image/jpeg")
                images.append(base64_img)
        
        if len(images) != 2:
            return "❌ 请上传2张图片（首帧和尾帧）"
        
        if not prompt.strip():
            return "❌ 请输入文本提示词"
        
        # 创建任务
        response = client.start_end_to_video(
            model=model,
            images=images,
            prompt=prompt.strip(),
            duration=int(duration),
            seed=seed if seed != 0 else None,
            resolution=resolution,
            movement_amplitude=convert_movement_amplitude(movement_amplitude),  # 转换中文为英文
            bgm=bgm == "有"
        )
        if not isinstance(response, dict) or 'task_id' not in response:
            return f"❌ 创建任务失败，API返回: {response}"
        task_id = response['task_id']
        
        # 立即显示任务ID
        result = f"✅ 起止生视频任务创建成功！<br>任务ID: {task_id}<br>"
        result += "⏳ 正在等待任务完成...<br>"
        
        start_time = time.time()
        while True:
            # 查询任务状态
            task_info = client.query_task(task_id)
            if not isinstance(task_info, dict):
                return f"❌ 查询任务状态失败: {task_info}"
            
            state = task_info.get('state')
            elapsed_time = int(time.time() - start_time)
            
            if state == ViduTaskStatus.SUCCESS:
                # 任务完成，提供下载链接
                result = f"✅ 起止生视频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"✅ 任务完成！耗时: {elapsed_time}秒<br>"
                result += "📥 请点击以下链接下载文件：<br><br>"
                
                # 获取下载链接
                try:
                    creations = client.get_creations(task_info)
                    if creations:
                        for creation in creations:
                            if creation.get('url'):
                                result += f"🎬 <a href='{creation['url']}' target='_blank' style='color: #007bff; text-decoration: none;'>点击下载视频</a><br><br>"
                            if creation.get('cover_url'):
                                result += f"🖼️ <a href='{creation['cover_url']}' target='_blank' style='color: #007bff; text-decoration: none;'>点击下载封面</a><br><br>"
                except Exception as link_error:
                    result += f"⚠️ 获取下载链接失败: {str(link_error)}<br>"
                    result += "💡 请稍后重试或联系技术支持<br>"
                break
            elif state == ViduTaskStatus.FAILED:
                err_code = task_info.get('err_code', '未知错误')
                result = f"✅ 起止生视频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 任务失败: {get_error_message(err_code)}<br>"
                break
            elif state in [ViduTaskStatus.CREATED, ViduTaskStatus.QUEUEING, ViduTaskStatus.PROCESSING]:
                # 更新等待时间
                result = f"✅ 起止生视频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"⏳ 正在等待任务完成... 已等待: {elapsed_time}秒<br>"
                time.sleep(1)  # 等待1秒
            else:
                result = f"✅ 起止生视频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 未知任务状态: {state}<br>"
                break
        
        return result
        
    except Exception as e:
        return f"❌ 创建任务失败: {str(e)}"


def create_start_end_to_video_ui(client: ViduClient):
    """创建起止生视频UI界面"""
    with gr.Tab("🎬 起止生视频"):
        with gr.Row():
            start2end_model = gr.Dropdown(
                choices=[m.value for m in ViduModel],
                value=ViduModel.VIDU1_5.value,
                label="模型"
            )
        
        start2end_images = gr.File(
            file_count="multiple",
            label="上传图片（必须2张：首帧和尾帧）",
            file_types=["image"]
        )
        
        start2end_prompt = gr.Textbox(
            label="文本提示词（必填）",
            placeholder="描述您想要的视频效果...",
            lines=3
        )
        
        with gr.Row():
            start2end_duration = gr.Dropdown(
                choices=["4", "8"],
                value="4",
                label="视频时长（秒）"
            )
            start2end_seed = gr.Number(
                value=0, label="随机种子（0表示随机）"
            )
        
        with gr.Row():
            start2end_resolution = gr.Dropdown(
                choices=get_start_end_resolution_options(ViduModel.VIDU1_5.value, "4"),
                value=get_start_end_default_resolution(ViduModel.VIDU1_5.value, "4"),
                label="分辨率"
            )
            start2end_movement = gr.Dropdown(
                choices=["自动", "小幅度", "中幅度", "大幅度"],
                value="自动",
                label="运动幅度"
            )
            start2end_bgm = gr.Dropdown(
                choices=["无", "有"],
                value="无",
                label="背景音乐"
            )
        
        start2end_btn = gr.Button("创建起止生视频任务", variant="primary")
        start2end_status = gr.HTML(label="状态", visible=False)
        start2end_output = gr.HTML(label="任务结果")
        
        def start2end_task(model, images, prompt, duration, seed, resolution, movement, bgm):
            return (
                gr.HTML(value="<div style='color: #007bff; font-weight: bold;'>⏳ 生成中，请耐心等待...</div>", visible=True),
                gr.HTML(value=""),
                gr.Button(interactive=False),
                gr.Dropdown(interactive=False),
                gr.File(interactive=False),
                gr.Textbox(interactive=False),
                gr.Dropdown(interactive=False),
                gr.Number(interactive=False),
                gr.Dropdown(interactive=False),
                gr.Dropdown(interactive=False),
                gr.Dropdown(interactive=False)
            )
        
        def start2end_complete(result):
            return (
                gr.HTML(visible=False),
                gr.HTML(value=result),
                gr.Button(interactive=True),
                gr.Dropdown(interactive=True),
                gr.File(interactive=True),
                gr.Textbox(interactive=True),
                gr.Dropdown(interactive=True),
                gr.Number(interactive=True),
                gr.Dropdown(interactive=True),
                gr.Dropdown(interactive=True),
                gr.Dropdown(interactive=True)
            )
        
        start2end_btn.click(
            fn=start2end_task,
            inputs=[start2end_model, start2end_images, start2end_prompt, 
                   start2end_duration, start2end_seed, start2end_resolution, 
                   start2end_movement, start2end_bgm],
            outputs=[start2end_status, start2end_output, start2end_btn, start2end_model, 
                   start2end_images, start2end_prompt, start2end_duration, 
                   start2end_seed, start2end_resolution, start2end_movement, start2end_bgm],
            queue=False
        ).then(
            fn=lambda *args: create_start_end_to_video_task(client, *args),
            inputs=[start2end_model, start2end_images, start2end_prompt, 
                   start2end_duration, start2end_seed, start2end_resolution, 
                   start2end_movement, start2end_bgm],
            outputs=[start2end_output]
        ).then(
            fn=start2end_complete,
            inputs=[start2end_output],
            outputs=[start2end_status, start2end_output, start2end_btn, start2end_model, 
                   start2end_images, start2end_prompt, start2end_duration, 
                   start2end_seed, start2end_resolution, start2end_movement, start2end_bgm]
        )
        
        # 绑定模型变化事件
        start2end_model.change(
            fn=lambda x: gr.Dropdown(choices=update_duration_options(x), value=update_duration_options(x)[0]),
            inputs=[start2end_model],
            outputs=[start2end_duration]
        )
        
        # 绑定模型和时长变化事件，更新分辨率选项
        def update_start_end_resolution_options(model, duration):
            options = get_start_end_resolution_options(model, duration)
            default = get_start_end_default_resolution(model, duration)
            return gr.Dropdown(choices=options, value=default)
        
        start2end_model.change(
            fn=update_start_end_resolution_options,
            inputs=[start2end_model, start2end_duration],
            outputs=[start2end_resolution]
        )
        
        start2end_duration.change(
            fn=update_start_end_resolution_options,
            inputs=[start2end_model, start2end_duration],
            outputs=[start2end_resolution]
        )
        
        return {
            'model': start2end_model,
            'images': start2end_images,
            'prompt': start2end_prompt,
            'duration': start2end_duration,
            'seed': start2end_seed,
            'resolution': start2end_resolution,
            'movement': start2end_movement,
            'bgm': start2end_bgm,
            'btn': start2end_btn,
            'status': start2end_status,
            'output': start2end_output
        } 
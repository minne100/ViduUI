#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能超清功能模块
包含UI界面和业务逻辑
"""

import gradio as gr
import time
from vidu_client import ViduClient, ViduTaskStatus
from utils import get_error_message


def create_upscale_pro_task(client: ViduClient, video_url: str, video_creation_id: str, upscale_resolution: str) -> str:
    """创建智能超清任务并轮询结果"""
    try:
        # 参数验证
        if not video_url.strip() and not video_creation_id.strip():
            return "❌ 请输入视频URL或视频创建ID"
        
        # 创建任务
        response = client.upscale_pro(
            video_url=video_url.strip() if video_url.strip() else None,
            video_creation_id=video_creation_id.strip() if video_creation_id.strip() else None,
            upscale_resolution=upscale_resolution
        )
        if not isinstance(response, dict) or 'task_id' not in response:
            return f"❌ 创建任务失败，API返回: {response}"
        task_id = response['task_id']
        
        # 立即显示任务ID
        result = f"✅ 智能超清任务创建成功！<br>任务ID: {task_id}<br>"
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
                result = f"✅ 智能超清任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"✅ 任务完成！耗时: {elapsed_time}秒<br>"
                result += "📥 请点击以下链接下载文件：<br><br>"
                
                # 获取下载链接
                try:
                    creations = client.get_creations(task_info)
                    if creations:
                        for creation in creations:
                            if creation.get('url'):
                                result += f"🎬 <a href='{creation['url']}' target='_blank' style='color: #007bff; text-decoration: none;'>点击下载视频</a><br><br>"
                except Exception as link_error:
                    result += f"⚠️ 获取下载链接失败: {str(link_error)}<br>"
                    result += "💡 请稍后重试或联系技术支持<br>"
                break
            elif state == ViduTaskStatus.FAILED:
                err_code = task_info.get('err_code', '未知错误')
                result = f"✅ 智能超清任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 任务失败: {get_error_message(err_code)}<br>"
                break
            elif state in [ViduTaskStatus.CREATED, ViduTaskStatus.QUEUEING, ViduTaskStatus.PROCESSING]:
                # 更新等待时间
                result = f"✅ 智能超清任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"⏳ 正在等待任务完成... 已等待: {elapsed_time}秒<br>"
                time.sleep(1)  # 等待1秒
            else:
                result = f"✅ 智能超清任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 未知任务状态: {state}<br>"
                break
        
        return result
        
    except Exception as e:
        return f"❌ 创建任务失败: {str(e)}"


def create_upscale_pro_ui(client: ViduClient):
    """创建智能超清UI界面"""
    with gr.Tab("🔍 智能超清"):
        with gr.Row():
            upscale_video_url = gr.Textbox(
                label="视频URL（可选）",
                placeholder="请输入要超清的视频URL",
                lines=2,
                info="支持的格式：MP4、FLV、HLS、MXF、MOV、TS、WEBM、MKV，时长不超过300秒，帧率低于60FPS"
            )
            upscale_video_creation_id = gr.Textbox(
                label="视频创建ID（可选）",
                placeholder="请输入Vidu视频生成任务的唯一ID",
                info="优先使用此参数，若同时填写则忽略视频URL"
            )
        
        upscale_resolution = gr.Dropdown(
            choices=["1080p", "2K", "4K", "8K"],
            value="1080p",
            label="目标输出分辨率",
            info="设置的清晰度必须高于原视频分辨率"
        )
        
        upscale_btn = gr.Button("创建智能超清任务", variant="primary")
        upscale_status = gr.HTML(label="状态", visible=False)
        upscale_output = gr.HTML(label="任务结果")
        
        def upscale_task(video_url, video_creation_id, upscale_resolution):
            return (
                gr.HTML(value="<div style='color: #007bff; font-weight: bold;'>⏳ 生成中，请耐心等待...</div>", visible=True),
                gr.HTML(value=""),
                gr.Button(interactive=False),
                gr.Textbox(interactive=False),
                gr.Textbox(interactive=False),
                gr.Dropdown(interactive=False)
            )
        
        def upscale_complete(result):
            return (
                gr.HTML(visible=False),
                gr.HTML(value=result),
                gr.Button(interactive=True),
                gr.Textbox(interactive=True),
                gr.Textbox(interactive=True),
                gr.Dropdown(interactive=True)
            )
        
        upscale_btn.click(
            fn=upscale_task,
            inputs=[upscale_video_url, upscale_video_creation_id, upscale_resolution],
            outputs=[upscale_status, upscale_output, upscale_btn, upscale_video_url, upscale_video_creation_id, upscale_resolution],
            queue=False
        ).then(
            fn=lambda *args: create_upscale_pro_task(client, *args),
            inputs=[upscale_video_url, upscale_video_creation_id, upscale_resolution],
            outputs=[upscale_output]
        ).then(
            fn=upscale_complete,
            inputs=[upscale_output],
            outputs=[upscale_status, upscale_output, upscale_btn, upscale_video_url, upscale_video_creation_id, upscale_resolution]
        )
        
        return {
            'video_url': upscale_video_url,
            'video_creation_id': upscale_video_creation_id,
            'upscale_resolution': upscale_resolution,
            'btn': upscale_btn,
            'status': upscale_status,
            'output': upscale_output
        } 
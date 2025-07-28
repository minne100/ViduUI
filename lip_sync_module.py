#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对口型功能模块
包含UI界面和业务逻辑
"""

import gradio as gr
import time
from vidu_client import ViduClient, ViduTaskStatus
from utils import get_error_message, get_voice_character_choices, get_voice_character_id
from file_upload_utils import save_uploaded_file, cleanup_files


def create_lip_sync_task(client: ViduClient, video_file: gr.File, drive_mode: str, audio_file: gr.File, 
                         text: str, speed: float, character_id: str, volume: int) -> str:
    """创建对口型任务并轮询结果"""
    uploaded_files = []  # 记录上传的文件路径，用于后续清理
    
    try:
        # 参数验证
        if not video_file or not video_file.name:
            return "❌ 请上传视频文件"
        
        if drive_mode == "音频驱动":
            if not audio_file or not audio_file.name:
                return "❌ 音频驱动模式下请上传音频文件"
        else:  # 文本驱动
            if not text.strip():
                return "❌ 文本驱动模式下请输入文本内容"
            if len(text.strip()) < 4:
                return "❌ 文本内容不能少于4个字符"
            if len(text.strip()) > 2000:
                return "❌ 文本内容不能超过2000个字符"
        
        # 上传视频文件
        video_result = save_uploaded_file(video_file, "video")
        if not video_result:
            return "❌ 视频文件上传失败"
        video_path, video_url = video_result
        uploaded_files.append(video_path)
        
        # 上传音频文件（如果是音频驱动模式）
        audio_url = None
        if drive_mode == "音频驱动" and audio_file and audio_file.name:
            audio_result = save_uploaded_file(audio_file, "audio")
            if not audio_result:
                cleanup_files(uploaded_files)
                return "❌ 音频文件上传失败"
            audio_path, audio_url = audio_result
            uploaded_files.append(audio_path)
        
        # 处理音色ID
        actual_character_id = None
        if drive_mode == "文本驱动" and character_id:
            actual_character_id = get_voice_character_id(character_id)
        
        # 创建任务
        response = client.lip_sync(
            video_url=video_url,
            audio_url=audio_url,
            text=text.strip() if drive_mode == "文本驱动" and text.strip() else None,
            speed=speed if drive_mode == "文本驱动" else None,
            character_id=actual_character_id,
            volume=volume if drive_mode == "文本驱动" else None
        )
        if not isinstance(response, dict) or 'task_id' not in response:
            return f"❌ 创建任务失败，API返回: {response}"
        task_id = response['task_id']
        
        # 立即显示任务ID
        result = f"✅ 对口型任务创建成功！<br>任务ID: {task_id}<br>"
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
                result = f"✅ 对口型任务创建成功！<br>任务ID: {task_id}<br>"
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
                result = f"✅ 对口型任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 任务失败: {get_error_message(err_code)}<br>"
                break
            elif state in [ViduTaskStatus.CREATED, ViduTaskStatus.QUEUEING, ViduTaskStatus.PROCESSING]:
                # 更新等待时间
                result = f"✅ 对口型任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"⏳ 正在等待任务完成... 已等待: {elapsed_time}秒<br>"
                time.sleep(1)  # 等待1秒
            else:
                result = f"✅ 对口型任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 未知任务状态: {state}<br>"
                break
        
        return result
        
    except Exception as e:
        # 清理已上传的文件
        cleanup_files(uploaded_files)
        return f"❌ 创建任务失败: {str(e)}"
    finally:
        # 任务完成后清理文件
        cleanup_files(uploaded_files)


def create_lip_sync_ui(client: ViduClient):
    """创建对口型UI界面"""
    with gr.Tab("👄 对口型"):
        lip_video_file = gr.File(
            label="上传视频文件（必填）",
            file_types=["video"]
        )
        gr.Markdown("💡 支持格式：mp4、mov、avi，时长1-600秒，建议10-120秒，文件大小不超过5G，编码格式H.264")
        
        lip_drive_mode = gr.Dropdown(
            choices=["音频驱动", "文本驱动"],
            value="音频驱动",
            label="驱动模式",
            info="音频驱动：使用音频文件，文本驱动：使用文本生成音频"
        )
        
        # 音频驱动模式的组件
        with gr.Group(visible=True) as audio_drive_group:
            with gr.Row():
                lip_audio_file = gr.File(
                    label="上传音频文件（音频驱动模式）",
                    file_types=["audio"]
                )
            gr.Markdown("💡 支持格式：wav、mp3、wma、m4a、aac、ogg，时长1-600秒，大小不超过100MB")
        
        # 文本驱动模式的组件
        with gr.Group(visible=False) as text_drive_group:
            with gr.Row():
                lip_text = gr.Textbox(
                    label="文本内容（文本驱动模式）",
                    placeholder="请输入要生成的文本内容",
                    lines=3
                )
            
            with gr.Row():
                lip_speed = gr.Slider(
                    minimum=0.5,
                    maximum=1.5,
                    value=1.0,
                    step=0.1,
                    label="语速（文本驱动模式）"
                )
                lip_character_id = gr.Dropdown(
                    choices=get_voice_character_choices(),
                    value="男声1 - 大方稳健 (male_1)",
                    label="音色选择（文本驱动模式）"
                )
            
            with gr.Row():
                lip_volume = gr.Slider(
                    minimum=0,
                    maximum=10,
                    value=0,
                    step=1,
                    label="音量（文本驱动模式）"
                )
            
            gr.Markdown("💡 文本内容4-2000字符，语速0.5最慢1.5最快，音量0为正常音量")
        lip_btn = gr.Button("创建对口型任务", variant="primary")
        lip_status = gr.HTML(label="状态", visible=False)
        lip_output = gr.HTML(label="任务结果")
        
        def lip_task(video_file, drive_mode, audio_file, text, speed, character_id, volume):
            return (
                gr.HTML(value="<div style='color: #007bff; font-weight: bold;'>⏳ 生成中，请耐心等待...</div>", visible=True),
                gr.HTML(value=""),
                gr.Button(interactive=False),
                gr.File(interactive=False),
                gr.Dropdown(interactive=False),
                gr.File(interactive=False),
                gr.Textbox(interactive=False),
                gr.Slider(interactive=False),
                gr.Dropdown(interactive=False),
                gr.Slider(interactive=False),
                gr.Group(interactive=False),
                gr.Group(interactive=False)
            )
        
        def lip_complete(result):
            return (
                gr.HTML(visible=False),
                gr.HTML(value=result),
                gr.Button(interactive=True),
                gr.File(interactive=True),
                gr.Dropdown(interactive=True),
                gr.File(interactive=True),
                gr.Textbox(interactive=True),
                gr.Slider(interactive=True),
                gr.Dropdown(interactive=True),
                gr.Slider(interactive=True),
                gr.Group(interactive=True),
                gr.Group(interactive=True)
            )
        
        def on_drive_mode_change(drive_mode):
            """根据驱动模式显示/隐藏相应组件"""
            if drive_mode == "音频驱动":
                return (
                    gr.Group(visible=True),  # 音频驱动组件
                    gr.Group(visible=False)   # 文本驱动组件
                )
            else:  # 文本驱动
                return (
                    gr.Group(visible=False),  # 音频驱动组件
                    gr.Group(visible=True)    # 文本驱动组件
                )
        
        # 绑定驱动模式变化事件
        lip_drive_mode.change(
            fn=on_drive_mode_change,
            inputs=[lip_drive_mode],
            outputs=[audio_drive_group, text_drive_group]
        )
        
        lip_btn.click(
            fn=lip_task,
            inputs=[lip_video_file, lip_drive_mode, lip_audio_file, lip_text, lip_speed, lip_character_id, lip_volume],
            outputs=[lip_status, lip_output, lip_btn, lip_video_file, lip_drive_mode, lip_audio_file, lip_text, lip_speed, lip_character_id, lip_volume, audio_drive_group, text_drive_group],
            queue=False
        ).then(
            fn=lambda *args: create_lip_sync_task(client, *args),
            inputs=[lip_video_file, lip_drive_mode, lip_audio_file, lip_text, lip_speed, lip_character_id, lip_volume],
            outputs=[lip_output]
        ).then(
            fn=lip_complete,
            inputs=[lip_output],
            outputs=[lip_status, lip_output, lip_btn, lip_video_file, lip_drive_mode, lip_audio_file, lip_text, lip_speed, lip_character_id, lip_volume, audio_drive_group, text_drive_group]
        )
        
        return {
            'video_file': lip_video_file,
            'drive_mode': lip_drive_mode,
            'audio_file': lip_audio_file,
            'text': lip_text,
            'speed': lip_speed,
            'character_id': lip_character_id,
            'volume': lip_volume,
            'btn': lip_btn,
            'status': lip_status,
            'output': lip_output
        } 
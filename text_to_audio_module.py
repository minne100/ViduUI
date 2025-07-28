#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文生音频功能模块
包含UI界面和业务逻辑
"""

import gradio as gr
import time
from vidu_client import ViduClient, ViduAudioModel, ViduTaskStatus
from utils import get_error_message


def create_text_to_audio_task(client: ViduClient, model: str, prompt: str, duration: float, seed: int) -> str:
    """创建文生音频任务并轮询结果"""
    try:
        if not prompt.strip():
            return "❌ 请输入文本提示词"
        
        # 验证时长范围
        if duration < 2 or duration > 10:
            return "❌ 音频时长必须在2-10秒之间"
        
        # 创建任务
        response = client.text_to_audio(
            model=model,
            prompt=prompt.strip(),
            duration=duration,
            seed=seed if seed != 0 else None
        )
        if not isinstance(response, dict) or 'task_id' not in response:
            return f"❌ 创建任务失败，API返回: {response}"
        task_id = response['task_id']
        
        # 立即显示任务ID
        result = f"✅ 文生音频任务创建成功！<br>任务ID: {task_id}<br>"
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
                result = f"✅ 文生音频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"✅ 任务完成！耗时: {elapsed_time}秒<br>"
                result += "📥 请点击以下链接下载文件：<br><br>"
                
                # 获取下载链接
                try:
                    audio_url = client.get_audio_url(task_info)
                    if audio_url:
                        result += f"🔊 <a href='{audio_url}' target='_blank' style='color: #007bff; text-decoration: none;'>点击下载音频</a><br><br>"
                except Exception as link_error:
                    result += f"⚠️ 获取下载链接失败: {str(link_error)}<br>"
                    result += "💡 请稍后重试或联系技术支持<br>"
                break
            elif state == ViduTaskStatus.FAILED:
                err_code = task_info.get('err_code', '未知错误')
                result = f"✅ 文生音频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 任务失败: {get_error_message(err_code)}<br>"
                break
            elif state in [ViduTaskStatus.CREATED, ViduTaskStatus.QUEUEING, ViduTaskStatus.PROCESSING]:
                # 更新等待时间
                result = f"✅ 文生音频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"⏳ 正在等待任务完成... 已等待: {elapsed_time}秒<br>"
                time.sleep(1)  # 等待1秒
            else:
                result = f"✅ 文生音频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 未知任务状态: {state}<br>"
                break
        
        return result
        
    except Exception as e:
        return f"❌ 创建任务失败: {str(e)}"


def create_text_to_audio_ui(client: ViduClient):
    """创建文生音频UI界面"""
    with gr.Tab("🎵 文生音频"):
        with gr.Row():
            text2audio_model = gr.Dropdown(
                choices=["audio1.0"],  # 根据官方文档，只有audio1.0模型
                value="audio1.0",
                label="音频模型"
            )
        
        text2audio_prompt = gr.Textbox(
            label="文本提示词",
            placeholder="请输入要转换为音频的文本描述，例如：清晨的鸟叫声...",
            lines=5
        )
        
        with gr.Row():
            text2audio_duration = gr.Slider(
                minimum=2.0,
                maximum=10.0,
                value=10.0,
                step=0.5,
                label="音频时长（秒）",
                info="可选范围：2-10秒，默认10秒"
            )
            text2audio_seed = gr.Number(
                value=0,
                label="随机种子",
                info="0表示自动生成，固定值生成确定性结果"
            )
        
        text2audio_btn = gr.Button("创建文生音频任务", variant="primary")
        text2audio_status = gr.HTML(label="状态", visible=False)
        text2audio_output = gr.HTML(label="任务结果")
        
        def text2audio_task(model, prompt, duration, seed):
            return (
                gr.HTML(value="<div style='color: #007bff; font-weight: bold;'>⏳ 生成中，请耐心等待...</div>", visible=True),
                gr.HTML(value=""),
                gr.Button(interactive=False),
                gr.Dropdown(interactive=False),
                gr.Textbox(interactive=False),
                gr.Slider(interactive=False),
                gr.Number(interactive=False)
            )
        
        def text2audio_complete(result):
            return (
                gr.HTML(visible=False),
                gr.HTML(value=result),
                gr.Button(interactive=True),
                gr.Dropdown(interactive=True),
                gr.Textbox(interactive=True),
                gr.Slider(interactive=True),
                gr.Number(interactive=True)
            )
        
        text2audio_btn.click(
            fn=text2audio_task,
            inputs=[text2audio_model, text2audio_prompt, text2audio_duration, text2audio_seed],
            outputs=[text2audio_status, text2audio_output, text2audio_btn, text2audio_model,
                   text2audio_prompt, text2audio_duration, text2audio_seed],
            queue=False
        ).then(
            fn=lambda *args: create_text_to_audio_task(client, *args),
            inputs=[text2audio_model, text2audio_prompt, text2audio_duration, text2audio_seed],
            outputs=[text2audio_output]
        ).then(
            fn=text2audio_complete,
            inputs=[text2audio_output],
            outputs=[text2audio_status, text2audio_output, text2audio_btn, text2audio_model,
                   text2audio_prompt, text2audio_duration, text2audio_seed]
        )
        
        return {
            'model': text2audio_model,
            'prompt': text2audio_prompt,
            'duration': text2audio_duration,
            'seed': text2audio_seed,
            'btn': text2audio_btn,
            'status': text2audio_status,
            'output': text2audio_output
        } 
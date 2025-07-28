#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间控制音频功能模块
包含UI界面和业务逻辑
"""

import gradio as gr
import time
from vidu_client import ViduClient, ViduAudioModel, ViduTaskStatus
from utils import get_error_message


def create_timing_to_audio_task(client: ViduClient, model: str, duration: float, timing_prompts_json: str, seed: int) -> str:
    """创建时间控制音频任务并轮询结果"""
    try:
        import json
        
        # 参数验证
        if not timing_prompts_json.strip():
            return "❌ 请输入时间控制音效参数"
        
        # 验证时长范围
        if duration < 2 or duration > 10:
            return "❌ 音频时长必须在2-10秒之间"
        
        # 解析timing_prompts JSON
        try:
            timing_prompts = json.loads(timing_prompts_json)
            if not isinstance(timing_prompts, list):
                return "❌ timing_prompts必须是数组格式"
        except json.JSONDecodeError:
            return "❌ timing_prompts格式错误，请检查JSON格式"
        
        # 验证每个事件
        for i, event in enumerate(timing_prompts):
            if not isinstance(event, dict):
                return f"❌ 第{i+1}个事件必须是对象格式"
            
            required_fields = ['from', 'to', 'prompt']
            for field in required_fields:
                if field not in event:
                    return f"❌ 第{i+1}个事件缺少{field}字段"
            
            # 验证时间范围
            if event['from'] < 0 or event['to'] > duration:
                return f"❌ 第{i+1}个事件的时间范围必须在[0, {duration}]之间"
            
            if event['from'] >= event['to']:
                return f"❌ 第{i+1}个事件的from时间必须小于to时间"
            
            # 验证提示词长度
            if len(event['prompt']) > 1500:
                return f"❌ 第{i+1}个事件的提示词不能超过1500字符"
        
        # 创建任务
        response = client.timing_to_audio(
            model=model,
            duration=duration,
            timing_prompts=timing_prompts,
            seed=seed if seed != 0 else None
        )
        if not isinstance(response, dict) or 'task_id' not in response:
            return f"❌ 创建任务失败，API返回: {response}"
        task_id = response['task_id']
        
        # 立即显示任务ID
        result = f"✅ 时间控制音频任务创建成功！<br>任务ID: {task_id}<br>"
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
                result = f"✅ 时间控制音频任务创建成功！<br>任务ID: {task_id}<br>"
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
                result = f"✅ 时间控制音频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 任务失败: {get_error_message(err_code)}<br>"
                break
            elif state in [ViduTaskStatus.CREATED, ViduTaskStatus.QUEUEING, ViduTaskStatus.PROCESSING]:
                # 更新等待时间
                result = f"✅ 时间控制音频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"⏳ 正在等待任务完成... 已等待: {elapsed_time}秒<br>"
                time.sleep(1)  # 等待1秒
            else:
                result = f"✅ 时间控制音频任务创建成功！<br>任务ID: {task_id}<br>"
                result += f"❌ 未知任务状态: {state}<br>"
                break
        
        return result
        
    except Exception as e:
        return f"❌ 创建任务失败: {str(e)}"


def create_timing_to_audio_ui(client: ViduClient):
    """创建可控文生音效UI界面"""
    with gr.Tab("⏰ 可控文生音效"):
        with gr.Row():
            timing2audio_model = gr.Dropdown(
                choices=["audio1.0"],  # 根据官方文档，只支持audio1.0模型
                value="audio1.0",
                label="音频模型"
            )
            timing2audio_duration = gr.Slider(
                minimum=2.0,
                maximum=10.0,
                value=10.0,
                step=0.5,
                label="音频时长（秒）",
                info="可选范围：2-10秒，默认10秒"
            )
        
        timing2audio_timing_prompts = gr.Textbox(
            label="时间控制音效参数（JSON格式）",
            placeholder='''[
  {
    "from": 0.0,
    "to": 3.0,
    "prompt": "清晨的鸟叫声"
  },
  {
    "from": 3.0,
    "to": 6.0,
    "prompt": "远处传来火车驶过的声音"
  },
  {
    "from": 5.0,
    "to": 9.5,
    "prompt": "海浪轻轻拍打沙滩"
  }
]''',
            lines=15,
            info="支持多个事件重叠，单个事件提示词最大1500字符，from/to必须在[0, duration]区间内"
        )
        
        timing2audio_seed = gr.Number(
            value=0,
            label="随机种子",
            info="0表示自动生成，固定值生成确定性结果"
        )
        
        timing2audio_btn = gr.Button("创建时间控制音频任务", variant="primary")
        timing2audio_status = gr.HTML(label="状态", visible=False)
        timing2audio_output = gr.HTML(label="任务结果")
        
        def timing2audio_task(model, duration, timing_prompts, seed):
            return (
                gr.HTML(value="<div style='color: #007bff; font-weight: bold;'>⏳ 生成中，请耐心等待...</div>", visible=True),
                gr.HTML(value=""),
                gr.Button(interactive=False),
                gr.Dropdown(interactive=False),
                gr.Slider(interactive=False),
                gr.Textbox(interactive=False),
                gr.Number(interactive=False)
            )
        
        def timing2audio_complete(result):
            return (
                gr.HTML(visible=False),
                gr.HTML(value=result),
                gr.Button(interactive=True),
                gr.Dropdown(interactive=True),
                gr.Slider(interactive=True),
                gr.Textbox(interactive=True),
                gr.Number(interactive=True)
            )
        
        timing2audio_btn.click(
            fn=timing2audio_task,
            inputs=[timing2audio_model, timing2audio_duration, timing2audio_timing_prompts, timing2audio_seed],
            outputs=[timing2audio_status, timing2audio_output, timing2audio_btn, timing2audio_model,
                   timing2audio_duration, timing2audio_timing_prompts, timing2audio_seed],
            queue=False
        ).then(
            fn=lambda *args: create_timing_to_audio_task(client, *args),
            inputs=[timing2audio_model, timing2audio_duration, timing2audio_timing_prompts, timing2audio_seed],
            outputs=[timing2audio_output]
        ).then(
            fn=timing2audio_complete,
            inputs=[timing2audio_output],
            outputs=[timing2audio_status, timing2audio_output, timing2audio_btn, timing2audio_model,
                   timing2audio_duration, timing2audio_timing_prompts, timing2audio_seed]
        )
        
        return {
            'model': timing2audio_model,
            'duration': timing2audio_duration,
            'timing_prompts': timing2audio_timing_prompts,
            'seed': timing2audio_seed,
            'btn': timing2audio_btn,
            'status': timing2audio_status,
            'output': timing2audio_output
        } 
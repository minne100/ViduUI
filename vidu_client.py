"""
Vidu API Python客户端
支持图生视频、参考生视频、首尾帧生视频、文生视频、智能超清、对口型、文生音频、可控文生音效等功能
"""

import requests
import json
import time
import base64
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from enum import Enum

# 导入错误处理模块
from error_codes import ViduErrorHandler, ViduError


class ViduModel(str, Enum):
    """Vidu支持的模型枚举"""
    VIDUQ1 = "viduq1"
    VIDUQ1_CLASSIC = "viduq1-classic"
    VIDU2_0 = "vidu2.0"
    VIDU1_5 = "vidu1.5"


class ViduResolution(str, Enum):
    """分辨率枚举"""
    P360 = "360p"
    P720 = "720p"
    P1080 = "1080p"


class ViduAspectRatio(str, Enum):
    """宽高比枚举"""
    RATIO_16_9 = "16:9"
    RATIO_9_16 = "9:16"
    RATIO_1_1 = "1:1"


class ViduMovementAmplitude(str, Enum):
    """运动幅度枚举"""
    AUTO = "auto"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ViduTaskStatus(str, Enum):
    """任务状态枚举"""
    CREATED = "created"
    QUEUEING = "queueing"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class ViduAudioModel(str, Enum):
    """音频模型枚举"""
    AUDIO1_0 = "audio1.0"


class ViduClient:
    """Vidu API客户端类"""
    
    # 模型时长限制配置（图生视频）
    MODEL_DURATION_LIMITS = {
        ViduModel.VIDUQ1: [5],  # viduq1 只支持5秒
        ViduModel.VIDUQ1_CLASSIC: [5],  # viduq1-classic 只支持5秒
        ViduModel.VIDU2_0: [4, 8],  # vidu2.0 支持4秒和8秒（图生视频）
        ViduModel.VIDU1_5: [4, 8],  # vidu1.5 支持4秒和8秒
    }
    
    # 参考生视频模型时长限制配置
    REFERENCE_MODEL_DURATION_LIMITS = {
        ViduModel.VIDUQ1: [5],  # viduq1 只支持5秒
        ViduModel.VIDUQ1_CLASSIC: [5],  # viduq1-classic 只支持5秒
        ViduModel.VIDU2_0: [4],  # vidu2.0 只支持4秒（参考生视频）
        ViduModel.VIDU1_5: [4, 8],  # vidu1.5 支持4秒和8秒
    }
    
    # 首尾帧生视频模型时长限制配置
    START_END_MODEL_DURATION_LIMITS = {
        ViduModel.VIDUQ1: [5],  # viduq1 只支持5秒
        ViduModel.VIDUQ1_CLASSIC: [5],  # viduq1-classic 只支持5秒
        ViduModel.VIDU2_0: [4, 8],  # vidu2.0 支持4秒和8秒（首尾帧生视频）
        ViduModel.VIDU1_5: [4, 8],  # vidu1.5 支持4秒和8秒
    }
    
    # 文生视频模型时长限制配置
    TEXT_TO_VIDEO_MODEL_DURATION_LIMITS = {
        ViduModel.VIDUQ1: [5],  # viduq1 只支持5秒
        ViduModel.VIDU1_5: [4, 8],  # vidu1.5 支持4秒和8秒
    }
    
    # 模型默认时长
    MODEL_DEFAULT_DURATIONS = {
        ViduModel.VIDUQ1: 5,
        ViduModel.VIDUQ1_CLASSIC: 5,
        ViduModel.VIDU2_0: 4,
        ViduModel.VIDU1_5: 4,
    }
    
    def __init__(self, api_key: str, base_url: str = "https://api.vidu.cn"):
        """
        初始化Vidu客户端
        
        Args:
            api_key: Vidu API密钥
            base_url: API基础URL，默认为官方地址
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {api_key}',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            
        Returns:
            API响应数据
            
        Raises:
            ViduError: API返回的错误
            requests.RequestException: 网络请求异常
            ValueError: 请求参数错误
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            response_data = response.json()
            
            # 使用 error_codes.py 检查API响应中的错误
            ViduErrorHandler.handle_api_response(response_data)
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"API请求失败: {e}")
        except ViduError:
            # 重新抛出ViduError，保持错误类型
            raise
        except ValueError as e:
            raise ValueError(f"请求参数错误: {e}")
        except Exception as e:
            raise Exception(f"未知错误: {e}")
    
    def _validate_duration(self, model: Union[str, ViduModel], duration: Optional[int]) -> int:
        """
        验证并返回有效的视频时长（图生视频）
        
        Args:
            model: 模型名称
            duration: 用户指定的时长
            
        Returns:
            有效的视频时长
            
        Raises:
            ValueError: 时长验证失败
        """
        model_str = str(model)
        model_enum = ViduModel(model_str)
        
        # 如果没有指定时长，使用默认时长
        if duration is None:
            return self.MODEL_DEFAULT_DURATIONS[model_enum]
        
        # 检查时长是否在允许范围内
        if duration not in self.MODEL_DURATION_LIMITS[model_enum]:
            raise ValueError(f"模型 {model_str} 不支持 {duration} 秒时长，支持的时长: {self.MODEL_DURATION_LIMITS[model_enum]}")
        
        return duration
    
    def _validate_duration_for_reference(self, model: Union[str, ViduModel], duration: Optional[int]) -> int:
        """
        验证并返回有效的视频时长（参考生视频）
        
        Args:
            model: 模型名称
            duration: 用户指定的时长
            
        Returns:
            有效的视频时长
            
        Raises:
            ValueError: 时长验证失败
        """
        model_str = str(model)
        model_enum = ViduModel(model_str)
        
        # 如果没有指定时长，使用默认时长
        if duration is None:
            return self.MODEL_DEFAULT_DURATIONS[model_enum]
        
        # 检查时长是否在允许范围内
        allowed_durations = self.REFERENCE_MODEL_DURATION_LIMITS[model_enum]
        if duration not in allowed_durations:
            raise ValueError(
                f"模型 {model_str} 在参考生视频中不支持 {duration} 秒时长。"
                f"支持的时长: {allowed_durations} 秒"
            )
        
        return duration
    
    def _validate_duration_for_start_end(self, model: Union[str, ViduModel], duration: Optional[int]) -> int:
        """
        验证并返回有效的视频时长（首尾帧生视频）
        
        Args:
            model: 模型名称
            duration: 用户指定的时长
            
        Returns:
            有效的视频时长
            
        Raises:
            ValueError: 时长验证失败
        """
        model_str = str(model)
        model_enum = ViduModel(model_str)
        
        # 如果没有指定时长，使用默认时长
        if duration is None:
            return self.MODEL_DEFAULT_DURATIONS[model_enum]
        
        # 检查时长是否在允许范围内
        allowed_durations = self.START_END_MODEL_DURATION_LIMITS[model_enum]
        if duration not in allowed_durations:
            raise ValueError(
                f"模型 {model_str} 在首尾帧生视频中不支持 {duration} 秒时长。"
                f"支持的时长: {allowed_durations} 秒"
            )
        
        return duration
    
    def _validate_duration_for_text_to_video(self, model: Union[str, ViduModel], duration: Optional[int]) -> int:
        """
        验证并返回有效的视频时长（文生视频）
        
        Args:
            model: 模型名称
            duration: 用户指定的时长
            
        Returns:
            有效的视频时长
            
        Raises:
            ValueError: 时长验证失败
        """
        model_str = str(model)
        model_enum = ViduModel(model_str)
        
        # 如果没有指定时长，使用默认时长
        if duration is None:
            return self.MODEL_DEFAULT_DURATIONS[model_enum]
        
        # 检查时长是否在允许范围内
        allowed_durations = self.TEXT_TO_VIDEO_MODEL_DURATION_LIMITS[model_enum]
        if duration not in allowed_durations:
            raise ValueError(
                f"模型 {model_str} 在文生视频中不支持 {duration} 秒时长。"
                f"支持的时长: {allowed_durations} 秒"
            )
        
        return duration
    
    def image_to_video(
        self,
        model: Union[str, ViduModel],
        images: List[str],
        prompt: Optional[str] = None,
        duration: Optional[int] = None,
        seed: Optional[int] = None,
        resolution: Optional[Union[str, ViduResolution]] = None,
        movement_amplitude: Optional[Union[str, ViduMovementAmplitude]] = None,
        bgm: Optional[bool] = None,
        payload: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建图生视频任务
        
        Args:
            model: 模型名称 (viduq1, vidu2.0, vidu1.5)
            images: 首帧图像列表（支持Base64编码或URL）
            prompt: 文本提示词（可选，最大1500字符）
            duration: 视频时长（可选，根据模型有不同限制）
                - viduq1: 只支持5秒
                - vidu2.0: 只支持4秒
                - vidu1.5: 支持4秒和8秒
            seed: 随机种子（可选，0表示随机）
            resolution: 分辨率（可选）
            movement_amplitude: 运动幅度（可选）
            bgm: 是否添加背景音乐（可选）
            payload: 透传参数（可选，最大1048576字符）
            callback_url: 回调URL（可选）
            
        Returns:
            包含任务ID和状态的响应数据
            
        Raises:
            ValueError: 参数验证失败
            ViduError: API返回的错误
            requests.RequestException: API请求失败
        """
        # 参数验证
        if not images or len(images) != 1:
            raise ValueError("images参数必须包含且仅包含1张图片")
        
        if prompt and len(prompt) > 1500:
            raise ValueError("prompt参数不能超过1500个字符")
        
        if payload and len(payload) > 1048576:
            raise ValueError("payload参数不能超过1048576个字符")
        
        # 验证时长
        validated_duration = self._validate_duration(model, duration)
        
        # 构建请求数据
        request_data = {
            "model": str(model),
            "images": images,
            "duration": validated_duration
        }
        
        if prompt is not None:
            request_data["prompt"] = prompt
        
        if seed is not None:
            request_data["seed"] = seed
        
        if resolution is not None:
            request_data["resolution"] = str(resolution)
        
        if movement_amplitude is not None:
            request_data["movement_amplitude"] = str(movement_amplitude)
        
        if bgm is not None:
            request_data["bgm"] = bgm
        
        if payload is not None:
            request_data["payload"] = payload
        
        if callback_url is not None:
            request_data["callback_url"] = callback_url
        
        return self._make_request('POST', '/ent/v2/img2video', request_data)
    
    def reference_to_video(
        self,
        model: Union[str, ViduModel],
        images: List[str],
        prompt: str,
        duration: Optional[int] = None,
        seed: Optional[int] = None,
        aspect_ratio: Optional[Union[str, ViduAspectRatio]] = None,
        resolution: Optional[Union[str, ViduResolution]] = None,
        movement_amplitude: Optional[Union[str, ViduMovementAmplitude]] = None,
        bgm: Optional[bool] = None,
        payload: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建参考生视频任务
        
        Args:
            model: 模型名称 (viduq1, vidu2.0, vidu1.5)
            images: 图像参考列表（支持1-7张图片）
            prompt: 文本提示词（必填，最大1500字符）
            duration: 视频时长（可选，根据模型有不同限制）
                - viduq1: 只支持5秒
                - vidu2.0: 只支持4秒
                - vidu1.5: 支持4秒和8秒
            seed: 随机种子（可选，0表示随机）
            aspect_ratio: 宽高比（可选）
            resolution: 分辨率（可选）
            movement_amplitude: 运动幅度（可选）
            bgm: 是否添加背景音乐（可选）
            payload: 透传参数（可选，最大1048576字符）
            callback_url: 回调URL（可选）
            
        Returns:
            包含任务ID和状态的响应数据
            
        Raises:
            ValueError: 参数验证失败
            ViduError: API返回的错误
            requests.RequestException: API请求失败
        """
        # 参数验证
        if not images or len(images) < 1 or len(images) > 7:
            raise ValueError("images参数必须包含1-7张图片")
        
        if not prompt.strip():
            raise ValueError("prompt参数不能为空")
        
        if len(prompt) > 1500:
            raise ValueError("prompt参数不能超过1500个字符")
        
        if payload and len(payload) > 1048576:
            raise ValueError("payload参数不能超过1048576个字符")
        
        # 验证时长（使用参考生视频的时长限制）
        validated_duration = self._validate_duration_for_reference(model, duration)
        
        # 构建请求数据
        request_data = {
            "model": str(model),
            "images": images,
            "prompt": prompt,
            "duration": validated_duration
        }
        
        if seed is not None:
            request_data["seed"] = seed
        
        if aspect_ratio is not None:
            request_data["aspect_ratio"] = str(aspect_ratio)
        
        if resolution is not None:
            request_data["resolution"] = str(resolution)
        
        if movement_amplitude is not None:
            request_data["movement_amplitude"] = str(movement_amplitude)
        
        if bgm is not None:
            request_data["bgm"] = bgm
        
        if payload is not None:
            request_data["payload"] = payload
        
        if callback_url is not None:
            request_data["callback_url"] = callback_url
        
        return self._make_request('POST', '/ent/v2/reference2video', request_data)
    
    def start_end_to_video(
        self,
        model: Union[str, ViduModel],
        images: List[str],
        prompt: Optional[str] = None,
        duration: Optional[int] = None,
        seed: Optional[int] = None,
        resolution: Optional[Union[str, ViduResolution]] = None,
        movement_amplitude: Optional[Union[str, ViduMovementAmplitude]] = None,
        bgm: Optional[bool] = None,
        payload: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建首尾帧生视频任务
        
        Args:
            model: 模型名称 (viduq1, viduq1-classic, vidu2.0, vidu1.5)
            images: 首尾帧图像列表（必须包含2张图片）
            prompt: 文本提示词（可选，最大1500字符）
            duration: 视频时长（可选，根据模型有不同限制）
                - viduq1: 只支持5秒
                - viduq1-classic: 只支持5秒
                - vidu2.0: 支持4秒和8秒
                - vidu1.5: 支持4秒和8秒
            seed: 随机种子（可选，0表示随机）
            resolution: 分辨率（可选）
            movement_amplitude: 运动幅度（可选）
            bgm: 是否添加背景音乐（可选）
            payload: 透传参数（可选，最大1048576字符）
            callback_url: 回调URL（可选）
            
        Returns:
            包含任务ID和状态的响应数据
            
        Raises:
            ValueError: 参数验证失败
            requests.RequestException: API请求失败
        """
        # 参数验证
        if not images or len(images) != 2:
            raise ValueError("images参数必须包含且仅包含2张图片（首帧和尾帧）")
        
        if prompt and len(prompt) > 1500:
            raise ValueError("prompt参数不能超过1500个字符")
        
        if payload and len(payload) > 1048576:
            raise ValueError("payload参数不能超过1048576个字符")
        
        # 验证时长（使用首尾帧生视频的时长限制）
        validated_duration = self._validate_duration_for_start_end(model, duration)
        
        # 构建请求数据
        request_data = {
            "model": str(model),
            "images": images,
            "duration": validated_duration
        }
        
        if prompt is not None:
            request_data["prompt"] = prompt
        
        if seed is not None:
            request_data["seed"] = seed
        
        if resolution is not None:
            request_data["resolution"] = str(resolution)
        
        if movement_amplitude is not None:
            request_data["movement_amplitude"] = str(movement_amplitude)
        
        if bgm is not None:
            request_data["bgm"] = bgm
        
        if payload is not None:
            request_data["payload"] = payload
        
        if callback_url is not None:
            request_data["callback_url"] = callback_url
        
        return self._make_request('POST', '/ent/v2/start-end2video', request_data)
    
    def text_to_video(
        self,
        model: Union[str, ViduModel],
        style: str,
        prompt: str,
        duration: Optional[int] = None,
        seed: Optional[int] = None,
        aspect_ratio: Optional[Union[str, ViduAspectRatio]] = None,
        resolution: Optional[Union[str, ViduResolution]] = None,
        movement_amplitude: Optional[Union[str, ViduMovementAmplitude]] = None,
        bgm: Optional[bool] = None,
        payload: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建文生视频任务
        
        Args:
            model: 模型名称 (viduq1, vidu1.5)
            style: 风格 (general, anime)
            prompt: 文本提示词（必填，最大1500字符）
            duration: 视频时长（可选，根据模型有不同限制）
                - viduq1: 只支持5秒
                - vidu1.5: 支持4秒和8秒
            seed: 随机种子（可选，0表示随机）
            aspect_ratio: 宽高比（可选）
            resolution: 分辨率（可选）
            movement_amplitude: 运动幅度（可选）
            bgm: 是否添加背景音乐（可选）
            payload: 透传参数（可选，最大1048576字符）
            callback_url: 回调URL（可选）
            
        Returns:
            包含任务ID和状态的响应数据
            
        Raises:
            ValueError: 参数验证失败
            requests.RequestException: API请求失败
        """
        # 参数验证
        if not prompt.strip():
            raise ValueError("prompt参数不能为空")
        
        if len(prompt) > 1500:
            raise ValueError("prompt参数不能超过1500个字符")
        
        if style not in ["general", "anime"]:
            raise ValueError("style参数必须是 general 或 anime")
        
        if payload and len(payload) > 1048576:
            raise ValueError("payload参数不能超过1048576个字符")
        
        # 验证时长（使用文生视频的时长限制）
        validated_duration = self._validate_duration_for_text_to_video(model, duration)
        
        # 构建请求数据
        request_data = {
            "model": str(model),
            "style": style,
            "prompt": prompt,
            "duration": validated_duration
        }
        
        if seed is not None:
            request_data["seed"] = seed
        
        if aspect_ratio is not None:
            request_data["aspect_ratio"] = str(aspect_ratio)
        
        if resolution is not None:
            request_data["resolution"] = str(resolution)
        
        if movement_amplitude is not None:
            request_data["movement_amplitude"] = str(movement_amplitude)
        
        if bgm is not None:
            request_data["bgm"] = bgm
        
        if payload is not None:
            request_data["payload"] = payload
        
        if callback_url is not None:
            request_data["callback_url"] = callback_url
        
        return self._make_request('POST', '/ent/v2/text2video', request_data)
    
    def upscale_pro(
        self,
        video_url: Optional[str] = None,
        video_creation_id: Optional[str] = None,
        upscale_resolution: Optional[str] = None,
        payload: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建智能超清任务
        
        Args:
            video_url: 视频URL（可选）
            video_creation_id: Vidu视频生成任务的唯一ID（可选）
            upscale_resolution: 目标输出分辨率（可选，默认1080p）
            payload: 透传参数（可选，最大1048576字符）
            callback_url: 回调URL（可选）
            
        Returns:
            包含任务ID和状态的响应数据
            
        Raises:
            ValueError: 参数验证失败
            requests.RequestException: API请求失败
        """
        # 参数验证
        if not video_url and not video_creation_id:
            raise ValueError("video_url和video_creation_id参数至少需要提供一个")
        
        if upscale_resolution and upscale_resolution not in ["1080p", "2K", "4K", "8K"]:
            raise ValueError("upscale_resolution参数必须是 1080p、2K、4K、8K 中的一个")
        
        if payload and len(payload) > 1048576:
            raise ValueError("payload参数不能超过1048576个字符")
        
        # 构建请求数据
        request_data = {}
        
        if video_url:
            request_data["video_url"] = video_url
        
        if video_creation_id:
            request_data["video_creation_id"] = video_creation_id
        
        if upscale_resolution:
            request_data["upscale_resolution"] = upscale_resolution
        
        if payload is not None:
            request_data["payload"] = payload
        
        if callback_url is not None:
            request_data["callback_url"] = callback_url
        
        return self._make_request('POST', '/ent/v2/upscale-new', request_data)
    
    def lip_sync(
        self,
        video_url: str,
        audio_url: Optional[str] = None,
        text: Optional[str] = None,
        speed: Optional[float] = None,
        character_id: Optional[str] = None,
        volume: Optional[int] = None,
        language: Optional[str] = None,
        payload: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建对口型任务
        
        Args:
            video_url: 视频URL（必填）
            audio_url: 音频URL（可选，音频驱动模式）
            text: 文本内容（可选，文本驱动模式，4-2000字符）
            speed: 语速（可选，文本驱动模式，0.5-1.5，默认1.0）
            character_id: 音色ID（可选，文本驱动模式）
            volume: 音量（可选，文本驱动模式，0-10，默认0）
            language: 语种（可选，文本驱动模式）
            payload: 透传参数（可选，最大1048576字符）
            callback_url: 回调URL（可选）
            
        Returns:
            包含任务ID和状态的响应数据
            
        Raises:
            ValueError: 参数验证失败
            requests.RequestException: API请求失败
        """
        # 参数验证
        if not video_url:
            raise ValueError("video_url参数为必填项")
        
        # 检查驱动模式
        if not audio_url and not text:
            raise ValueError("audio_url和text参数至少需要提供一个")
        
        if text and (len(text) < 4 or len(text) > 2000):
            raise ValueError("text参数长度必须在4-2000字符之间")
        
        if speed is not None and (speed < 0.5 or speed > 1.5):
            raise ValueError("speed参数必须在0.5-1.5之间")
        
        if volume is not None and (volume < 0 or volume > 10):
            raise ValueError("volume参数必须在0-10之间")
        
        if payload and len(payload) > 1048576:
            raise ValueError("payload参数不能超过1048576个字符")
        
        # 构建请求数据
        request_data = {
            "video_url": video_url
        }
        
        if audio_url:
            request_data["audio_url"] = audio_url
        
        if text:
            request_data["text"] = text
        
        if speed is not None:
            request_data["speed"] = speed
        
        if character_id:
            request_data["character_id"] = character_id
        
        if volume is not None:
            request_data["volume"] = volume
        
        if language:
            request_data["language"] = language
        
        if payload is not None:
            request_data["payload"] = payload
        
        if callback_url is not None:
            request_data["callback_url"] = callback_url
        
        return self._make_request('POST', '/ent/v2/lip-sync', request_data)
    
    def text_to_audio(
        self,
        model: str,
        prompt: str,
        duration: Optional[float] = None,
        seed: Optional[int] = None,
        payload: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建文生音频任务
        
        Args:
            model: 音频模型名称 (audio1.0)
            prompt: 文本提示词（必填，最大1500字符）
            duration: 音频时长（可选，默认10秒，范围2-10秒）
            seed: 随机种子（可选，0表示自动生成）
            payload: 透传参数（可选，最大1048576字符）
            callback_url: 回调URL（可选）
            
        Returns:
            包含任务ID和状态的响应数据
            
        Raises:
            ValueError: 参数验证失败
            ViduError: API返回的错误
            requests.RequestException: API请求失败
        """
        # 参数验证
        if not prompt.strip():
            raise ValueError("prompt参数不能为空")
        
        if len(prompt) > 1500:
            raise ValueError("prompt参数不能超过1500个字符")
        
        if duration is not None and (duration < 2 or duration > 10):
            raise ValueError("duration参数必须在2-10秒之间")
        
        if payload and len(payload) > 1048576:
            raise ValueError("payload参数不能超过1048576个字符")
        
        # 构建请求数据
        request_data = {
            "model": str(model),
            "prompt": prompt
        }
        
        if duration is not None:
            request_data["duration"] = duration
        
        if seed is not None:
            request_data["seed"] = seed
        
        if payload is not None:
            request_data["payload"] = payload
        
        if callback_url is not None:
            request_data["callback_url"] = callback_url
        
        return self._make_request('POST', '/ent/v2/text2audio', request_data)
    
    def timing_to_audio(
        self,
        model: Union[str, ViduAudioModel],
        timing_prompts: List[Dict[str, Any]],
        duration: Optional[float] = None,
        seed: Optional[int] = None,
        payload: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建可控文生音效任务
        
        Args:
            model: 音频模型名称 (audio1.0)
            timing_prompts: 可控音效参数列表（必填），每个事件包含from、to、prompt字段
            duration: 音频时长（可选，默认10秒，范围2-10秒）
            seed: 随机种子（可选，0表示自动生成）
            payload: 透传参数（可选，最大1048576字符）
            callback_url: 回调URL（可选）
            
        Returns:
            包含任务ID和状态的响应数据
            
        Raises:
            ValueError: 参数验证失败
            requests.RequestException: API请求失败
        """
        # 参数验证
        if not timing_prompts:
            raise ValueError("timing_prompts参数不能为空")
        
        if duration is not None and (duration < 2 or duration > 10):
            raise ValueError("duration参数必须在2-10秒之间")
        
        # 验证每个事件
        for i, event in enumerate(timing_prompts):
            if not isinstance(event, dict):
                raise ValueError(f"第{i+1}个事件必须是对象格式")
            
            required_fields = ['from', 'to', 'prompt']
            for field in required_fields:
                if field not in event:
                    raise ValueError(f"第{i+1}个事件缺少{field}字段")
            
            # 验证时间范围
            actual_duration = duration or 10.0
            if event['from'] < 0 or event['to'] > actual_duration:
                raise ValueError(f"第{i+1}个事件的时间范围必须在[0, {actual_duration}]之间")
            
            if event['from'] >= event['to']:
                raise ValueError(f"第{i+1}个事件的from时间必须小于to时间")
            
            # 验证提示词长度
            if len(event['prompt']) > 1500:
                raise ValueError(f"第{i+1}个事件的提示词不能超过1500字符")
        
        if payload and len(payload) > 1048576:
            raise ValueError("payload参数不能超过1048576个字符")
        
        # 构建请求数据
        request_data = {
            "model": str(model),
            "timing_prompts": timing_prompts
        }
        
        if duration is not None:
            request_data["duration"] = duration
        
        if seed is not None:
            request_data["seed"] = seed
        
        if payload is not None:
            request_data["payload"] = payload
        
        if callback_url is not None:
            request_data["callback_url"] = callback_url
        
        return self._make_request('POST', '/ent/v2/timing2audio', request_data)
    
    def query_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
            
        Raises:
            ViduError: API返回的错误
            requests.RequestException: API请求失败
        """
        return self._make_request('GET', f'/ent/v2/tasks/{task_id}/creations')
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            取消结果
            
        Raises:
            ViduError: API返回的错误
            requests.RequestException: API请求失败
        """
        return self._make_request('POST', f'/ent/v2/task/{task_id}/cancel')
    
    def wait_for_completion(
        self, 
        task_id: str, 
        timeout: int = 300, 
        check_interval: int = 5
    ) -> Dict[str, Any]:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒），默认5分钟
            check_interval: 检查间隔（秒），默认5秒
            
        Returns:
            最终任务状态
            
        Raises:
            TimeoutError: 任务超时
            ViduError: API返回的错误
            requests.RequestException: API请求失败
        """
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"任务 {task_id} 超时（{timeout}秒）")
            
            task_info = self.query_task(task_id)
            status = task_info.get('state')
            
            if status in [ViduTaskStatus.SUCCESS, ViduTaskStatus.FAILED]:
                return task_info
            
            time.sleep(check_interval)
    
    @staticmethod
    def encode_image_to_base64(image_path: str, content_type: str = "image/png") -> str:
        """
        将图片文件编码为Base64格式
        
        Args:
            image_path: 图片文件路径
            content_type: 内容类型（如image/png, image/jpeg等）
            
        Returns:
            Base64编码的图片数据
            
        Raises:
            FileNotFoundError: 文件不存在
            IOError: 文件读取失败
        """
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                return f"data:{content_type};base64,{base64_data}"
        except FileNotFoundError:
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        except IOError as e:
            raise IOError(f"读取图片文件失败: {str(e)}")
    
    def get_creations(self, task_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从任务信息中获取生成物列表
        
        Args:
            task_info: 任务信息字典
            
        Returns:
            生成物列表，如果任务未完成则返回空列表
        """
        if task_info.get('state') == ViduTaskStatus.SUCCESS:
            return task_info.get('creations', [])
        return []
    
    def get_video_url(self, task_info: Dict[str, Any]) -> Optional[str]:
        """
        从任务信息中获取视频URL
        
        Args:
            task_info: 任务信息字典
            
        Returns:
            视频URL，如果任务未完成则返回None
        """
        creations = self.get_creations(task_info)
        if creations:
            return creations[0].get('url')
        return None
    
    def get_audio_url(self, task_info: Dict[str, Any]) -> Optional[str]:
        """
        从任务信息中获取音频URL
        
        Args:
            task_info: 任务信息字典
            
        Returns:
            音频URL，如果任务未完成则返回None
        """
        creations = self.get_creations(task_info)
        if creations:
            return creations[0].get('url')
        return None
    
    def get_cover_url(self, task_info: Dict[str, Any]) -> Optional[str]:
        """
        从任务信息中获取封面URL
        
        Args:
            task_info: 任务信息字典
            
        Returns:
            封面URL，如果任务未完成则返回None
        """
        creations = self.get_creations(task_info)
        if creations:
            return creations[0].get('cover_url')
        return None
    
    def download_file(self, url: str, save_path: str, chunk_size: int = 8192) -> str:
        """
        下载文件到指定路径
        
        Args:
            url: 文件URL
            save_path: 保存路径
            chunk_size: 下载块大小
            
        Returns:
            保存的文件路径
            
        Raises:
            requests.RequestException: 下载失败
            IOError: 文件保存失败
        """
        try:
            # 确保目录存在
            save_dir = os.path.dirname(save_path)
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
            
            # 下载文件
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            
            return save_path
            
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"下载文件失败: {str(e)}")
        except IOError as e:
            raise IOError(f"保存文件失败: {str(e)}")
    
    def download_creation(self, task_info: Dict[str, Any], save_dir: str = ".", 
                         filename_prefix: Optional[str] = None) -> Dict[str, str]:
        """
        下载任务的所有生成物
        
        Args:
            task_info: 任务信息字典
            save_dir: 保存目录，默认为当前目录
            filename_prefix: 文件名前缀，默认为任务ID
            
        Returns:
            包含下载文件路径的字典
            
        Raises:
            ValueError: 任务未完成或没有生成物
            requests.RequestException: 下载失败
            IOError: 文件保存失败
        """
        creations = self.get_creations(task_info)
        if not creations:
            raise ValueError("任务未完成或没有生成物")
        
        # 确保保存目录存在
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # 使用任务ID作为文件名前缀
        if filename_prefix is None:
            filename_prefix = task_info.get('id', 'creation')
        
        downloaded_files = {}
        
        for i, creation in enumerate(creations):
            creation_id = creation.get('id', f'creation_{i}')
            
            # 下载主文件
            if creation.get('url'):
                # 获取完整的URL（包含预签名参数）
                url = creation['url']
                
                # 从URL推断文件扩展名（移除查询参数后）
                url_for_ext = url
                if '?' in url_for_ext:
                    url_for_ext = url_for_ext.split('?')[0]
                
                # 尝试从URL获取扩展名，默认为mp4
                ext = '.mp4'
                if '.' in url_for_ext:
                    ext = '.' + url_for_ext.split('.')[-1]
                
                main_filename = f"{filename_prefix}_{creation_id}{ext}"
                main_path = str(save_path / main_filename)
                
                downloaded_files[f'main_{i}'] = self.download_file(url, main_path)
            
            # 下载封面文件
            if creation.get('cover_url'):
                # 获取完整的URL（包含预签名参数）
                cover_url = creation['cover_url']
                
                # 从URL推断文件扩展名（移除查询参数后）
                cover_url_for_ext = cover_url
                if '?' in cover_url_for_ext:
                    cover_url_for_ext = cover_url_for_ext.split('?')[0]
                
                # 尝试从URL获取扩展名，默认为jpg
                ext = '.jpg'
                if '.' in cover_url_for_ext:
                    ext = '.' + cover_url_for_ext.split('.')[-1]
                
                cover_filename = f"{filename_prefix}_{creation_id}_cover{ext}"
                cover_path = str(save_path / cover_filename)
                
                downloaded_files[f'cover_{i}'] = self.download_file(cover_url, cover_path)
        
        return downloaded_files
    
    def download_video(self, task_info: Dict[str, Any], save_path: str) -> str:
        """
        下载视频文件
        
        Args:
            task_info: 任务信息字典
            save_path: 保存路径
            
        Returns:
            保存的文件路径
            
        Raises:
            ValueError: 任务未完成或没有视频
            requests.RequestException: 下载失败
            IOError: 文件保存失败
        """
        video_url = self.get_video_url(task_info)
        if not video_url:
            raise ValueError("任务未完成或没有视频")
        
        return self.download_file(video_url, save_path)
    
    def download_audio(self, task_info: Dict[str, Any], save_path: str) -> str:
        """
        下载音频文件
        
        Args:
            task_info: 任务信息字典
            save_path: 保存路径
            
        Returns:
            保存的文件路径
            
        Raises:
            ValueError: 任务未完成或没有音频
            requests.RequestException: 下载失败
            IOError: 文件保存失败
        """
        audio_url = self.get_audio_url(task_info)
        if not audio_url:
            raise ValueError("任务未完成或没有音频")
        
        return self.download_file(audio_url, save_path)
    
    def download_cover(self, task_info: Dict[str, Any], save_path: str) -> str:
        """
        下载封面文件
        
        Args:
            task_info: 任务信息字典
            save_path: 保存路径
            
        Returns:
            保存的文件路径
            
        Raises:
            ValueError: 任务未完成或没有封面
            requests.RequestException: 下载失败
            IOError: 文件保存失败
        """
        cover_url = self.get_cover_url(task_info)
        if not cover_url:
            raise ValueError("任务未完成或没有封面")
        
        return self.download_file(cover_url, save_path)
    
    def create_task(self, task_id: str) -> 'ViduTask':
        """
        创建ViduTask对象
        
        Args:
            task_id: 任务ID
            
        Returns:
            ViduTask对象
        """
        return ViduTask(self, task_id)


class ViduTask:
    """Vidu任务包装类，提供便捷的任务管理功能"""
    
    def __init__(self, client: ViduClient, task_id: str):
        """
        初始化任务对象
        
        Args:
            client: Vidu客户端实例
            task_id: 任务ID
        """
        self.client = client
        self.task_id = task_id
        self._task_info = None
    
    def refresh(self) -> Dict[str, Any]:
        """
        刷新任务状态
        
        Returns:
            最新任务信息
        """
        self._task_info = self.client.query_task(self.task_id)
        return self._task_info
    
    @property
    def status(self) -> Optional[str]:
        """获取任务状态"""
        if self._task_info is None:
            self.refresh()
        return self._task_info.get('state') if self._task_info else None
    
    @property
    def is_completed(self) -> bool:
        """检查任务是否完成"""
        status = self.status
        return status in [ViduTaskStatus.SUCCESS, ViduTaskStatus.FAILED]
    
    @property
    def is_success(self) -> bool:
        """检查任务是否成功"""
        return self.status == ViduTaskStatus.SUCCESS
    
    @property
    def video_url(self) -> Optional[str]:
        """获取视频URL"""
        if self.is_success and self._task_info:
            return self.client.get_video_url(self._task_info)
        return None
    
    @property
    def audio_url(self) -> Optional[str]:
        """获取音频URL"""
        if self.is_success and self._task_info:
            return self.client.get_audio_url(self._task_info)
        return None
    
    @property
    def cover_url(self) -> Optional[str]:
        """获取封面URL"""
        if self.is_success and self._task_info:
            return self.client.get_cover_url(self._task_info)
        return None
    
    @property
    def creations(self) -> List[Dict[str, Any]]:
        """获取生成物列表"""
        if self.is_success and self._task_info:
            return self.client.get_creations(self._task_info)
        return []
    
    def wait_for_completion(self, timeout: int = 300, check_interval: int = 5) -> Dict[str, Any]:
        """
        等待任务完成
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            最终任务信息
        """
        self._task_info = self.client.wait_for_completion(
            self.task_id, timeout, check_interval
        )
        return self._task_info
    
    def download_creation(self, save_dir: str = ".", filename_prefix: Optional[str] = None) -> Dict[str, str]:
        """
        下载任务的所有生成物
        
        Args:
            save_dir: 保存目录，默认为当前目录
            filename_prefix: 文件名前缀，默认为任务ID
            
        Returns:
            包含下载文件路径的字典
            
        Raises:
            ValueError: 任务未完成或没有生成物
            requests.RequestException: 下载失败
            IOError: 文件保存失败
        """
        if not self.is_success or not self._task_info:
            raise ValueError("任务未完成或没有生成物")
        
        return self.client.download_creation(self._task_info, save_dir, filename_prefix)
    
    def download_video(self, save_path: str) -> str:
        """
        下载视频文件
        
        Args:
            save_path: 保存路径
            
        Returns:
            保存的文件路径
            
        Raises:
            ValueError: 任务未完成或没有视频
            requests.RequestException: 下载失败
            IOError: 文件保存失败
        """
        if not self.is_success or not self._task_info:
            raise ValueError("任务未完成或没有视频")
        
        return self.client.download_video(self._task_info, save_path)
    
    def download_audio(self, save_path: str) -> str:
        """
        下载音频文件
        
        Args:
            save_path: 保存路径
            
        Returns:
            保存的文件路径
            
        Raises:
            ValueError: 任务未完成或没有音频
            requests.RequestException: 下载失败
            IOError: 文件保存失败
        """
        if not self.is_success or not self._task_info:
            raise ValueError("任务未完成或没有音频")
        
        return self.client.download_audio(self._task_info, save_path)
    
    def download_cover(self, save_path: str) -> str:
        """
        下载封面文件
        
        Args:
            save_path: 保存路径
            
        Returns:
            保存的文件路径
            
        Raises:
            ValueError: 任务未完成或没有封面
            requests.RequestException: 下载失败
            IOError: 文件保存失败
        """
        if not self.is_success or not self._task_info:
            raise ValueError("任务未完成或没有封面")
        
        return self.client.download_cover(self._task_info, save_path)
    
    def cancel(self) -> Dict[str, Any]:
        """
        取消任务
        
        Returns:
            取消结果
        """
        return self.client.cancel_task(self.task_id)
    
    def __str__(self) -> str:
        return f"ViduTask(task_id={self.task_id}, status={self.status})"
    
    def __repr__(self) -> str:
        return self.__str__() 
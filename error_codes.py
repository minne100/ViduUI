"""
Vidu API 错误码处理模块
包含所有错误码定义和对应的处理方式
"""

from enum import Enum
from typing import Dict, Optional


class ViduErrorCode(str, Enum):
    """Vidu API 错误码枚举"""
    
    # 成功
    SUCCESS = "0"
    
    # 参数错误 (400)
    INVALID_PARAMETER = "400"
    MISSING_REQUIRED_PARAMETER = "400001"
    INVALID_MODEL = "400002"
    INVALID_IMAGE_FORMAT = "400003"
    INVALID_IMAGE_SIZE = "400004"
    INVALID_IMAGE_RATIO = "400005"
    INVALID_PROMPT_LENGTH = "400006"
    INVALID_DURATION = "400007"
    INVALID_RESOLUTION = "400008"
    INVALID_ASPECT_RATIO = "400009"
    INVALID_MOVEMENT_AMPLITUDE = "400010"
    INVALID_SEED = "400011"
    INVALID_PAYLOAD_LENGTH = "400012"
    INVALID_CALLBACK_URL = "400013"
    INVALID_VIDEO_URL = "400014"
    INVALID_AUDIO_URL = "400015"
    INVALID_VOICE_ID = "400016"
    INVALID_TIMING_PARAMETERS = "400017"
    
    # 认证错误 (401)
    UNAUTHORIZED = "401"
    INVALID_API_KEY = "401001"
    API_KEY_EXPIRED = "401002"
    INVALID_TOKEN = "401003"
    
    # 权限错误 (403)
    FORBIDDEN = "403"
    INSUFFICIENT_PERMISSIONS = "403001"
    ACCOUNT_SUSPENDED = "403002"
    RATE_LIMIT_EXCEEDED = "403003"
    QUOTA_EXCEEDED = "403004"
    
    # 资源错误 (404)
    NOT_FOUND = "404"
    TASK_NOT_FOUND = "404001"
    MODEL_NOT_FOUND = "404002"
    VOICE_NOT_FOUND = "404003"
    
    # 请求频率错误 (429)
    TOO_MANY_REQUESTS = "429"
    RATE_LIMIT_HIT = "429001"
    
    # 服务器错误 (500)
    INTERNAL_SERVER_ERROR = "500"
    SERVICE_UNAVAILABLE = "500001"
    PROCESSING_ERROR = "500002"
    MODEL_ERROR = "500003"
    STORAGE_ERROR = "500004"
    
    # 任务状态错误
    TASK_ALREADY_COMPLETED = "409001"
    TASK_ALREADY_CANCELLED = "409002"
    TASK_IN_PROGRESS = "409003"
    
    # 文件错误
    FILE_TOO_LARGE = "413001"
    UNSUPPORTED_FILE_FORMAT = "415001"
    FILE_CORRUPTED = "422001"


class ViduError(Exception):
    """Vidu API 自定义异常类"""
    
    def __init__(self, error_code: str, message: str, details: Optional[Dict] = None):
        """
        初始化Vidu错误
        
        Args:
            error_code: 错误码
            message: 错误消息
            details: 错误详情
        """
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        return f"ViduError({self.error_code}): {self.message}"
    
    def __repr__(self) -> str:
        return f"ViduError(error_code='{self.error_code}', message='{self.message}', details={self.details})"


class ViduErrorHandler:
    """Vidu API 错误处理器"""
    
    # 错误码到错误消息的映射
    ERROR_MESSAGES = {
        ViduErrorCode.SUCCESS: "操作成功",
        
        # 参数错误
        ViduErrorCode.INVALID_PARAMETER: "请求参数错误",
        ViduErrorCode.MISSING_REQUIRED_PARAMETER: "缺少必需参数",
        ViduErrorCode.INVALID_MODEL: "无效的模型名称",
        ViduErrorCode.INVALID_IMAGE_FORMAT: "无效的图片格式",
        ViduErrorCode.INVALID_IMAGE_SIZE: "图片大小超出限制",
        ViduErrorCode.INVALID_IMAGE_RATIO: "图片比例不符合要求",
        ViduErrorCode.INVALID_PROMPT_LENGTH: "提示词长度超出限制",
        ViduErrorCode.INVALID_DURATION: "无效的视频时长",
        ViduErrorCode.INVALID_RESOLUTION: "无效的分辨率",
        ViduErrorCode.INVALID_ASPECT_RATIO: "无效的宽高比",
        ViduErrorCode.INVALID_MOVEMENT_AMPLITUDE: "无效的运动幅度",
        ViduErrorCode.INVALID_SEED: "无效的随机种子",
        ViduErrorCode.INVALID_PAYLOAD_LENGTH: "透传参数长度超出限制",
        ViduErrorCode.INVALID_CALLBACK_URL: "无效的回调URL",
        ViduErrorCode.INVALID_VIDEO_URL: "无效的视频URL",
        ViduErrorCode.INVALID_AUDIO_URL: "无效的音频URL",
        ViduErrorCode.INVALID_VOICE_ID: "无效的声音ID",
        ViduErrorCode.INVALID_TIMING_PARAMETERS: "无效的时间控制参数",
        
        # 认证错误
        ViduErrorCode.UNAUTHORIZED: "认证失败",
        ViduErrorCode.INVALID_API_KEY: "无效的API密钥",
        ViduErrorCode.API_KEY_EXPIRED: "API密钥已过期",
        ViduErrorCode.INVALID_TOKEN: "无效的访问令牌",
        
        # 权限错误
        ViduErrorCode.FORBIDDEN: "权限不足",
        ViduErrorCode.INSUFFICIENT_PERMISSIONS: "权限不足",
        ViduErrorCode.ACCOUNT_SUSPENDED: "账户已被暂停",
        ViduErrorCode.RATE_LIMIT_EXCEEDED: "请求频率超出限制",
        ViduErrorCode.QUOTA_EXCEEDED: "配额已用完",
        
        # 资源错误
        ViduErrorCode.NOT_FOUND: "资源不存在",
        ViduErrorCode.TASK_NOT_FOUND: "任务不存在",
        ViduErrorCode.MODEL_NOT_FOUND: "模型不存在",
        ViduErrorCode.VOICE_NOT_FOUND: "声音不存在",
        
        # 请求频率错误
        ViduErrorCode.TOO_MANY_REQUESTS: "请求过于频繁",
        ViduErrorCode.RATE_LIMIT_HIT: "达到请求频率限制",
        
        # 服务器错误
        ViduErrorCode.INTERNAL_SERVER_ERROR: "服务器内部错误",
        ViduErrorCode.SERVICE_UNAVAILABLE: "服务不可用",
        ViduErrorCode.PROCESSING_ERROR: "处理过程中发生错误",
        ViduErrorCode.MODEL_ERROR: "模型处理错误",
        ViduErrorCode.STORAGE_ERROR: "存储错误",
        
        # 任务状态错误
        ViduErrorCode.TASK_ALREADY_COMPLETED: "任务已完成",
        ViduErrorCode.TASK_ALREADY_CANCELLED: "任务已取消",
        ViduErrorCode.TASK_IN_PROGRESS: "任务正在进行中",
        
        # 文件错误
        ViduErrorCode.FILE_TOO_LARGE: "文件过大",
        ViduErrorCode.UNSUPPORTED_FILE_FORMAT: "不支持的文件格式",
        ViduErrorCode.FILE_CORRUPTED: "文件损坏",
    }
    
    # 错误码到HTTP状态码的映射
    HTTP_STATUS_CODES = {
        ViduErrorCode.INVALID_PARAMETER: 400,
        ViduErrorCode.MISSING_REQUIRED_PARAMETER: 400,
        ViduErrorCode.INVALID_MODEL: 400,
        ViduErrorCode.INVALID_IMAGE_FORMAT: 400,
        ViduErrorCode.INVALID_IMAGE_SIZE: 400,
        ViduErrorCode.INVALID_IMAGE_RATIO: 400,
        ViduErrorCode.INVALID_PROMPT_LENGTH: 400,
        ViduErrorCode.INVALID_DURATION: 400,
        ViduErrorCode.INVALID_RESOLUTION: 400,
        ViduErrorCode.INVALID_ASPECT_RATIO: 400,
        ViduErrorCode.INVALID_MOVEMENT_AMPLITUDE: 400,
        ViduErrorCode.INVALID_SEED: 400,
        ViduErrorCode.INVALID_PAYLOAD_LENGTH: 400,
        ViduErrorCode.INVALID_CALLBACK_URL: 400,
        ViduErrorCode.INVALID_VIDEO_URL: 400,
        ViduErrorCode.INVALID_AUDIO_URL: 400,
        ViduErrorCode.INVALID_VOICE_ID: 400,
        ViduErrorCode.INVALID_TIMING_PARAMETERS: 400,
        
        ViduErrorCode.UNAUTHORIZED: 401,
        ViduErrorCode.INVALID_API_KEY: 401,
        ViduErrorCode.API_KEY_EXPIRED: 401,
        ViduErrorCode.INVALID_TOKEN: 401,
        
        ViduErrorCode.FORBIDDEN: 403,
        ViduErrorCode.INSUFFICIENT_PERMISSIONS: 403,
        ViduErrorCode.ACCOUNT_SUSPENDED: 403,
        ViduErrorCode.RATE_LIMIT_EXCEEDED: 403,
        ViduErrorCode.QUOTA_EXCEEDED: 403,
        
        ViduErrorCode.NOT_FOUND: 404,
        ViduErrorCode.TASK_NOT_FOUND: 404,
        ViduErrorCode.MODEL_NOT_FOUND: 404,
        ViduErrorCode.VOICE_NOT_FOUND: 404,
        
        ViduErrorCode.TOO_MANY_REQUESTS: 429,
        ViduErrorCode.RATE_LIMIT_HIT: 429,
        
        ViduErrorCode.INTERNAL_SERVER_ERROR: 500,
        ViduErrorCode.SERVICE_UNAVAILABLE: 500,
        ViduErrorCode.PROCESSING_ERROR: 500,
        ViduErrorCode.MODEL_ERROR: 500,
        ViduErrorCode.STORAGE_ERROR: 500,
        
        ViduErrorCode.TASK_ALREADY_COMPLETED: 409,
        ViduErrorCode.TASK_ALREADY_CANCELLED: 409,
        ViduErrorCode.TASK_IN_PROGRESS: 409,
        
        ViduErrorCode.FILE_TOO_LARGE: 413,
        ViduErrorCode.UNSUPPORTED_FILE_FORMAT: 415,
        ViduErrorCode.FILE_CORRUPTED: 422,
    }
    
    @classmethod
    def get_error_message(cls, error_code: str) -> str:
        """
        获取错误码对应的错误消息
        
        Args:
            error_code: 错误码
            
        Returns:
            错误消息
        """
        return cls.ERROR_MESSAGES.get(error_code, f"未知错误: {error_code}")
    
    @classmethod
    def get_http_status_code(cls, error_code: str) -> int:
        """
        获取错误码对应的HTTP状态码
        
        Args:
            error_code: 错误码
            
        Returns:
            HTTP状态码
        """
        return cls.HTTP_STATUS_CODES.get(error_code, 500)
    
    @classmethod
    def create_error(cls, error_code: str, details: Optional[Dict] = None) -> ViduError:
        """
        创建Vidu错误对象
        
        Args:
            error_code: 错误码
            details: 错误详情
            
        Returns:
            ViduError对象
        """
        message = cls.get_error_message(error_code)
        return ViduError(error_code, message, details)
    
    @classmethod
    def handle_api_response(cls, response_data: Dict) -> None:
        """
        处理API响应，检查是否有错误
        
        Args:
            response_data: API响应数据
            
        Raises:
            ViduError: 如果响应包含错误
        """
        if "error_code" in response_data and response_data["error_code"] != "0":
            error_code = response_data["error_code"]
            details = response_data.get("details", {})
            raise cls.create_error(error_code, details)
    
    @classmethod
    def is_retryable_error(cls, error_code: str) -> bool:
        """
        判断错误是否可重试
        
        Args:
            error_code: 错误码
            
        Returns:
            是否可重试
        """
        retryable_codes = {
            ViduErrorCode.SERVICE_UNAVAILABLE,
            ViduErrorCode.INTERNAL_SERVER_ERROR,
            ViduErrorCode.PROCESSING_ERROR,
            ViduErrorCode.MODEL_ERROR,
            ViduErrorCode.STORAGE_ERROR,
            ViduErrorCode.TOO_MANY_REQUESTS,
            ViduErrorCode.RATE_LIMIT_HIT,
        }
        return error_code in retryable_codes
    
    @classmethod
    def get_retry_delay(cls, error_code: str, attempt: int) -> int:
        """
        获取重试延迟时间（秒）
        
        Args:
            error_code: 错误码
            attempt: 重试次数
            
        Returns:
            延迟时间（秒）
        """
        base_delays = {
            ViduErrorCode.TOO_MANY_REQUESTS: 60,
            ViduErrorCode.RATE_LIMIT_HIT: 30,
            ViduErrorCode.SERVICE_UNAVAILABLE: 5,
            ViduErrorCode.INTERNAL_SERVER_ERROR: 2,
            ViduErrorCode.PROCESSING_ERROR: 2,
            ViduErrorCode.MODEL_ERROR: 2,
            ViduErrorCode.STORAGE_ERROR: 2,
        }
        
        base_delay = base_delays.get(error_code, 1)
        # 指数退避策略
        return min(base_delay * (2 ** (attempt - 1)), 300)  # 最大5分钟
    
    @classmethod
    def get_suggested_action(cls, error_code: str) -> str:
        """
        获取错误码对应的建议操作
        
        Args:
            error_code: 错误码
            
        Returns:
            建议操作
        """
        action_map = {
            ViduErrorCode.INVALID_API_KEY: "请检查API密钥是否正确",
            ViduErrorCode.API_KEY_EXPIRED: "请更新API密钥",
            ViduErrorCode.QUOTA_EXCEEDED: "请升级账户或等待配额重置",
            ViduErrorCode.RATE_LIMIT_EXCEEDED: "请降低请求频率",
            ViduErrorCode.INVALID_IMAGE_SIZE: "请确保图片大小不超过50MB",
            ViduErrorCode.INVALID_IMAGE_RATIO: "请确保图片比例在1:4到4:1之间",
            ViduErrorCode.INVALID_PROMPT_LENGTH: "请缩短提示词，确保不超过1500字符",
            ViduErrorCode.INVALID_PAYLOAD_LENGTH: "请缩短透传参数，确保不超过1048576字符",
            ViduErrorCode.TASK_NOT_FOUND: "请检查任务ID是否正确",
            ViduErrorCode.MODEL_NOT_FOUND: "请检查模型名称是否正确",
            ViduErrorCode.VOICE_NOT_FOUND: "请检查声音ID是否正确",
            ViduErrorCode.FILE_TOO_LARGE: "请压缩文件或使用较小的文件",
            ViduErrorCode.UNSUPPORTED_FILE_FORMAT: "请使用支持的图片格式（png、jpeg、jpg、webp）",
            ViduErrorCode.SERVICE_UNAVAILABLE: "请稍后重试",
            ViduErrorCode.INTERNAL_SERVER_ERROR: "请稍后重试，如果问题持续存在请联系技术支持",
        }
        
        return action_map.get(error_code, "请检查请求参数并重试")


def handle_vidu_error(error_code: str, details: Optional[Dict] = None) -> ViduError:
    """
    便捷函数：创建Vidu错误对象
    
    Args:
        error_code: 错误码
        details: 错误详情
        
    Returns:
        ViduError对象
    """
    return ViduErrorHandler.create_error(error_code, details)


def is_retryable_error(error_code: str) -> bool:
    """
    便捷函数：判断错误是否可重试
    
    Args:
        error_code: 错误码
        
    Returns:
        是否可重试
    """
    return ViduErrorHandler.is_retryable_error(error_code)


def get_error_suggestion(error_code: str) -> str:
    """
    便捷函数：获取错误建议
    
    Args:
        error_code: 错误码
        
    Returns:
        建议操作
    """
    return ViduErrorHandler.get_suggested_action(error_code) 
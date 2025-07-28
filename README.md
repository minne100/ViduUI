# Vidu API Python客户端

一个功能完整的Vidu API Python客户端，支持图生视频、参考生视频、首尾帧生视频、文生视频、智能超清、对口型、文生音频、可控文生音效等功能，并支持自动下载生成物和生成物封面。同时提供基于Gradio的Web UI界面。

## 功能特性

- ✅ 支持所有Vidu API功能
- ✅ 自动参数验证和错误处理
- ✅ 支持任务状态监控和等待
- ✅ **新增：自动下载生成物和生成物封面**
- ✅ 支持批量下载多个任务
- ✅ 支持本地文件处理（Base64编码）
- ✅ 完整的类型提示和文档
- ✅ **新增：基于Gradio的Web UI界面**
- ✅ **新增：自动任务完成和下载**
- ✅ **新增：.env文件配置支持**

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 方法一：使用Web UI界面（推荐）

#### 1. 配置API密钥

复制 `env_example.txt` 为 `.env` 文件，并设置您的Vidu API密钥：

```bash
# 复制示例文件
cp env_example.txt .env

# 编辑.env文件，设置您的API密钥
VIDU_API_KEY=your_api_key_here
```

或者设置环境变量：

```bash
export VIDU_API_KEY="your_api_key_here"
```

#### 2. 启动UI

```bash
# 方法1: 使用启动脚本
python start_ui.py

# 方法2: 直接运行UI文件
python vidu_ui.py
```

#### 3. 访问界面

启动后，在浏览器中访问：
- 本地访问: http://localhost:7860
- 公网访问: 启动后会显示链接

### 方法二：使用Python客户端

#### 基本使用

```python
from vidu_client import ViduClient, ViduModel, ViduTaskStatus

# 初始化客户端
client = ViduClient("your_api_key_here")

# 创建文生视频任务
response = client.text_to_video(
    model=ViduModel.VIDU1_5,
    prompt="一只可爱的小猫在花园里玩耍",
    duration=4
)

task_id = response['id']
print(f"任务创建成功，ID: {task_id}")

# 等待任务完成
task_info = client.wait_for_completion(task_id)

# 下载生成物
if task_info['state'] == ViduTaskStatus.SUCCESS:
    # 下载所有生成物（包括视频和封面）
    downloaded_files = client.download_creation(
        task_info, 
        save_dir="./downloads", 
        filename_prefix=f"video_{task_id}"
    )
    print(f"下载完成: {downloaded_files}")
```

#### 使用ViduTask类

```python
from vidu_client import ViduTask

# 创建任务对象
task = ViduTask(client, task_id)

# 等待完成并下载
task.wait_for_completion()
if task.is_success:
    # 下载视频
    video_path = task.download_video("./downloads/video.mp4")
    
    # 下载封面
    cover_path = task.download_cover("./downloads/cover.jpg")
    
    # 或者下载所有生成物
    all_files = task.download_creation("./downloads")
```

## Web UI界面功能

### 🎥 视频生成标签页

**功能**: 创建各种类型的视频生成任务，系统会自动等待完成并下载文件

#### 图生视频 (Image to Video)

**功能**: 根据上传的图片生成视频

**参数说明**:
- **模型**: 选择视频生成模型 (viduq1, vidu2.0, vidu1.5)
- **上传图片**: 支持1张图片上传
- **文本提示词**: 描述视频效果的文本（可选）
- **视频时长**: 4-8秒（根据模型限制）
- **随机种子**: 控制生成结果的随机性（0表示随机）
- **分辨率**: 视频分辨率 (360p, 720p, 1080p)
- **运动幅度**: 视频运动幅度 (auto, small, medium, large)
- **背景音乐**: 是否添加背景音乐

**使用步骤**:
1. 选择模型
2. 上传图片文件
3. 填写提示词（可选）
4. 调整其他参数
5. 点击"创建图生视频任务"

#### 参考生视频 (Reference to Video)

**功能**: 根据多张参考图片生成视频

**参数说明**:
- **模型**: 选择视频生成模型
- **参考图片**: 上传1-7张参考图片
- **文本提示词**: 必填，描述视频效果
- **宽高比**: 视频宽高比 (16:9, 9:16, 1:1)
- 其他参数同图生视频

#### 首尾帧生视频 (Start-End to Video)

**功能**: 根据首帧和尾帧图片生成视频

**参数说明**:
- **首帧图片**: 视频开始帧
- **尾帧图片**: 视频结束帧
- 其他参数同图生视频

#### 文生视频 (Text to Video)

**功能**: 根据文本描述生成视频

**参数说明**:
- **文本提示词**: 必填，描述要生成的视频内容
- 其他参数同参考生视频

### 🎬 视频处理标签页

#### 智能超清 (Upscale Pro)

**功能**: 提升视频分辨率

**参数说明**:
- **视频URL**: 要处理的视频URL

#### 对口型 (Lip Sync)

**功能**: 为视频添加口型同步

**参数说明**:
- **视频URL**: 视频文件URL
- **音频URL**: 音频文件URL

### 🎵 音频生成标签页

#### 文生音频 (Text to Audio)

**功能**: 将文本转换为音频

**参数说明**:
- **音频模型**: vidu-audio 或 vidu-audio-pro
- **文本内容**: 要转换的文本
- **声音ID**: 可选的声音ID

#### 可控文生音效 (Timing to Audio)

**功能**: 生成带时间控制的音频

**参数说明**:
- **时间控制参数**: JSON格式的时间控制参数
- 其他参数同文生音频

**时间控制参数示例**:
```json
[
  {
    "start_time": 0.0,
    "end_time": 2.0,
    "text": "欢迎"
  },
  {
    "start_time": 2.0,
    "end_time": 4.0,
    "text": "使用"
  }
]
```

### 📖 帮助标签页

包含详细的使用说明和注意事项。

## 下载功能详解

### 1. 下载所有生成物

```python
# 下载任务的所有生成物（包括视频和封面）
downloaded_files = client.download_creation(
    task_info, 
    save_dir="./downloads", 
    filename_prefix="my_video"
)

# 返回格式: {'main_0': 'path/to/video.mp4', 'cover_0': 'path/to/cover.jpg'}
```

### 2. 分别下载视频和封面

```python
# 下载视频文件
video_path = client.download_video(task_info, "./downloads/video.mp4")

# 下载封面文件
cover_path = client.download_cover(task_info, "./downloads/cover.jpg")
```

### 3. 批量下载多个任务

```python
task_ids = ["task_1", "task_2", "task_3"]

for i, task_id in enumerate(task_ids):
    task_info = client.query_task(task_id)
    
    if task_info['state'] == ViduTaskStatus.SUCCESS:
        # 为每个任务创建单独目录
        save_dir = f"./downloads/batch_{i+1}"
        downloaded_files = client.download_creation(
            task_info, 
            save_dir=save_dir,
            filename_prefix=f"batch_{i+1}"
        )
        print(f"任务 {task_id} 下载完成")
```

### 4. 使用ViduTask类的下载方法

```python
task = ViduTask(client, task_id)
task.wait_for_completion()

if task.is_success:
    # 获取URL信息
    print(f"视频URL: {task.video_url}")
    print(f"封面URL: {task.cover_url}")
    print(f"生成物数量: {len(task.creations)}")
    
    # 下载文件
    video_path = task.download_video("./downloads/video.mp4")
    cover_path = task.download_cover("./downloads/cover.jpg")
    all_files = task.download_creation("./downloads")
```

## API响应结构

根据Vidu API文档，查询任务接口返回的数据结构如下：

```json
{
  "id": "your_task_id",
  "state": "success",
  "err_code": "",
  "credits": 4,
  "payload": "",
  "creations": [
    {
      "id": "your_creations_id",
      "url": "your_generated_results_url",
      "cover_url": "your_generated_results_cover_url"
    }
  ]
}
```

## 支持的功能

### 视频生成
- **图生视频** (`image_to_video`)
- **参考生视频** (`reference_to_video`)
- **首尾帧生视频** (`start_end_to_video`)
- **文生视频** (`text_to_video`)

### 视频处理
- **智能超清** (`upscale_pro`)
- **对口型** (`lip_sync`)

### 音频生成
- **文生音频** (`text_to_audio`)
- **可控文生音效** (`timing_to_audio`)

### 任务管理
- **查询任务状态** (`query_task`)
- **取消任务** (`cancel_task`)
- **等待任务完成** (`wait_for_completion`)

### 下载功能
- **下载所有生成物** (`download_creation`)
- **下载视频文件** (`download_video`)
- **下载音频文件** (`download_audio`)
- **下载封面文件** (`download_cover`)

## 模型支持

| 模型 | 支持时长 | 支持功能 |
|------|----------|----------|
| viduq1 | 5秒 | 图生视频、参考生视频、首尾帧生视频、文生视频 |
| viduq1-classic | 5秒 | 首尾帧生视频 |
| vidu2.0 | 4秒 | 图生视频、参考生视频、首尾帧生视频、文生视频 |
| vidu1.5 | 4秒、8秒 | 图生视频、参考生视频、首尾帧生视频、文生视频 |

## 配置选项

### 环境变量

可以通过环境变量配置UI行为：

```bash
# 设置服务器端口
export VIDU_SERVER_PORT=8080

# 启用公网分享
export VIDU_SHARE_PUBLIC=true

# 设置默认超时时间
export VIDU_DEFAULT_TIMEOUT=600
```

### 配置文件

编辑 `config.py` 文件可以修改更多配置：

- 服务器配置
- UI主题
- 文件上传限制
- 下载目录
- 超时时间

## 文件结构

```
ViduUI/
├── vidu_ui.py          # 主UI文件
├── start_ui.py         # 启动脚本
├── config.py           # 配置文件
├── vidu_client.py      # Vidu API客户端
├── requirements.txt    # 依赖包列表
├── env_example.txt     # 环境变量示例文件
├── downloads/          # 下载文件目录
├── temp/              # 临时文件目录
└── README.md          # 本使用指南
```

## 错误处理

客户端提供了完善的错误处理机制：

```python
try:
    # 创建任务
    response = client.text_to_video(
        model=ViduModel.VIDU1_5,
        prompt="测试视频",
        duration=4
    )
    
    # 等待完成
    task_info = client.wait_for_completion(response['id'])
    
    # 下载文件
    if task_info['state'] == ViduTaskStatus.SUCCESS:
        downloaded_files = client.download_creation(task_info)
        print("下载成功")
    else:
        print(f"任务失败: {task_info.get('err_code')}")
        
except ValueError as e:
    print(f"参数错误: {e}")
except requests.RequestException as e:
    print(f"网络错误: {e}")
except TimeoutError as e:
    print(f"超时错误: {e}")
except IOError as e:
    print(f"文件操作错误: {e}")
```

## 常见问题

### Q: 如何获取Vidu API密钥？
A: 访问 [Vidu平台](https://platform.vidu.cn) 注册账号并获取API密钥。

### Q: 如何设置API密钥？
A: 复制 `env_example.txt` 为 `.env` 文件，并在其中设置 `VIDU_API_KEY=your_api_key_here`，或者设置环境变量 `VIDU_API_KEY`。

### Q: 任务创建失败怎么办？
A: 检查API密钥是否正确，网络连接是否稳定，参数是否符合要求。

### Q: 下载文件失败怎么办？
A: 检查磁盘空间是否充足，网络连接是否稳定。

### Q: 如何修改UI主题？
A: 在 `.env` 文件中设置 `VIDU_UI_THEME=soft`，或在 `config.py` 中修改 `UI_THEME` 参数，可选值：default, soft, glass, monochrome。

### Q: 如何启用公网访问？
A: 在 `.env` 文件中设置 `VIDU_SHARE_PUBLIC=true`，或在 `config.py` 中设置 `SHARE_PUBLIC = True`。

## 注意事项

1. **API密钥安全**: 请妥善保管您的API密钥，不要泄露给他人
2. **网络连接**: 确保网络连接稳定，特别是下载大文件时
3. **磁盘空间**: 确保有足够的磁盘空间存储下载的文件
4. **任务超时**: 长时间任务可能需要较长时间，请耐心等待
5. **自动下载**: 任务完成后会自动下载文件，无需手动操作
6. **文件权限**: 确保对下载目录有写入权限
7. **URL有效期**: 生成物的URL有1小时有效期，请及时下载

## 技术支持

如果遇到问题，请检查：
1. 依赖包是否正确安装
2. 配置文件是否正确
3. 网络连接是否正常
4. API密钥是否有效

更多信息请参考项目文档和Vidu API官方文档。

## 更新日志

### v3.0.0
- ✅ 新增基于Gradio的Web UI界面
- ✅ 新增自动任务完成和下载功能
- ✅ 新增.env文件配置支持
- ✅ 移除手动任务管理功能
- ✅ 简化用户操作流程

### v2.0.0
- ✅ 新增自动下载生成物和生成物封面功能
- ✅ 更新查询任务接口端点
- ✅ 添加ViduTask类的下载方法
- ✅ 支持批量下载多个任务
- ✅ 完善错误处理和文档

### v1.0.0
- ✅ 支持所有Vidu API功能
- ✅ 完整的参数验证
- ✅ 任务状态监控
- ✅ 类型提示和文档

## 许可证

MIT License 
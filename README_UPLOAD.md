# 上传 LoRA 到 Hugging Face 指南

## 准备工作

### 1. 从 Google Drive 下载 LoRA 文件

在 Colab 或本地执行：
```python
# 如果在 Colab
from google.colab import files
files.download('/content/drive/MyDrive/lora-training/output/pytorch_lora_weights.safetensors')
```

或者直接在 Google Drive 网页下载该文件。

### 2. 安装 Hugging Face Hub

```bash
pip install huggingface_hub
```

### 3. 获取 Access Token

1. 访问 https://huggingface.co/settings/tokens
2. 点击 "New token"
3. 选择 "Write" 权限
4. 复制生成的 token

## 上传步骤

### 方式 1：使用脚本（推荐）

```bash
python upload_to_hf.py
```

按提示输入：
- Hugging Face Token
- 仓库名称（例如：simple-icons-lora）
- 用户名
- LoRA 文件路径

### 方式 2：使用 Hugging Face 网页

1. 访问 https://huggingface.co/new
2. 创建新的 Model 仓库
3. 点击 "Files and versions" → "Add file" → "Upload files"
4. 上传 `pytorch_lora_weights.safetensors`
5. 编辑 README.md（可以参考脚本生成的内容）

### 方式 3：使用 Git LFS

```bash
# 克隆仓库
git clone https://huggingface.co/YOUR_USERNAME/YOUR_REPO_NAME
cd YOUR_REPO_NAME

# 复制 LoRA 文件
cp /path/to/pytorch_lora_weights.safetensors .

# 提交并推送
git add pytorch_lora_weights.safetensors
git commit -m "Upload LoRA weights"
git push
```

## 后续优化计划

### 短期优化（v2）

1. **调整训练参数**
   - 降低学习率：1e-4 → 5e-5
   - 减少 epochs：5 → 2
   - 增加 rank：8 → 32
   - 提高分辨率：384 → 512

2. **改进数据集**
   - 增加数据多样性
   - 添加数据增强
   - 改进 prompt 质量

3. **测试不同配置**
   - 尝试不同的 LoRA scale
   - 测试不同的推理参数
   - 收集用户反馈

### 中期优化（v3）

1. **扩展数据集**
   - 增加到 500+ 样本
   - 包含更多风格变化
   - 添加颜色变化

2. **训练策略改进**
   - 使用更好的学习率调度
   - 实验不同的 rank 值
   - 添加正则化

3. **质量评估**
   - 建立评估指标
   - 用户测试
   - A/B 测试不同版本

### 长期规划

1. **创建完整的 Logo 生成系统**
   - 多种风格 LoRA
   - 自动化训练 pipeline
   - Web 界面

2. **社区建设**
   - 收集用户生成的作品
   - 建立 Discord/论坛
   - 定期更新模型

## 使用示例

### 基础使用

```python
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
).to("cuda")

pipe.load_lora_weights("YOUR_USERNAME/simple-icons-lora")

image = pipe(
    "minimalist tech logo of React, geometric shape, flat design, single color",
    num_inference_steps=50,
    guidance_scale=12.0
).images[0]
```

### 高级使用

```python
# 调整 LoRA 强度
pipe.fuse_lora(lora_scale=0.8)  # 0.5-1.5 之间

# 使用 negative prompt
image = pipe(
    prompt="minimalist tech logo of Python",
    negative_prompt="blurry, low quality, distorted, complex",
    num_inference_steps=50,
    guidance_scale=12.0
).images[0]
```

## 推广策略

1. **在 Hugging Face 上**
   - 添加好看的示例图片
   - 写清楚的使用说明
   - 标注正确的 tags

2. **社交媒体**
   - Twitter/X 上分享
   - Reddit r/StableDiffusion
   - 中文社区（知乎、即刻）

3. **技术博客**
   - 写训练过程分享
   - 分享遇到的问题和解决方案
   - 开源训练代码和数据处理流程

## 版本管理

建议的版本命名：
- v1.0：当前版本（已训练完成）
- v2.0：改进参数后的版本
- v3.0：扩展数据集后的版本

每个版本创建单独的文件夹或 branch。

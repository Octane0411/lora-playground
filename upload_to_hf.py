"""
上传 LoRA 模型到 Hugging Face
使用方法：python upload_to_hf.py
"""

from huggingface_hub import HfApi, create_repo
import os
from pathlib import Path

# 配置信息
HF_TOKEN = input("请输入你的 Hugging Face Token: ").strip()
REPO_NAME = input("请输入仓库名称（例如：simple-icons-lora）: ").strip()
USERNAME = input("请输入你的 Hugging Face 用户名: ").strip()

# LoRA 文件路径（从 Google Drive 下载后的本地路径）
LORA_PATH = input("请输入 LoRA 文件路径（.safetensors）: ").strip()

# 创建 API 实例
api = HfApi(token=HF_TOKEN)

# 完整的仓库 ID
repo_id = f"{USERNAME}/{REPO_NAME}"

print(f"\n开始上传到: {repo_id}")

try:
    # 创建仓库（如果不存在）
    print("创建仓库...")
    create_repo(
        repo_id=repo_id,
        token=HF_TOKEN,
        repo_type="model",
        exist_ok=True
    )
    print("✓ 仓库创建成功")

    # 上传 LoRA 文件
    print("上传 LoRA 权重文件...")
    api.upload_file(
        path_or_fileobj=LORA_PATH,
        path_in_repo="pytorch_lora_weights.safetensors",
        repo_id=repo_id,
        token=HF_TOKEN
    )
    print("✓ LoRA 文件上传成功")

    # 创建 README
    readme_content = f"""---
license: other
license_name: stable-diffusion-xl-1.0-license
license_link: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/LICENSE.md
base_model: stabilityai/stable-diffusion-xl-base-1.0
tags:
  - stable-diffusion-xl
  - stable-diffusion-xl-diffusers
  - text-to-image
  - diffusers
  - lora
  - template:sd-lora
instance_prompt: minimalist tech logo
widget:
- text: 'minimalist tech logo of React, geometric shape, flat design, single color'
---

# Simple Icons LoRA for SDXL

A LoRA model trained on Simple Icons dataset for generating minimalist tech logos.

## Model Details

- **Base Model**: Stable Diffusion XL 1.0
- **Training Data**: 187 Simple Icons logos
- **Training Steps**: 120 steps (5 epochs)
- **Resolution**: 384x384
- **Rank**: 8
- **Learning Rate**: 1e-4

## Usage

```python
from diffusers import DiffusionPipeline
import torch

# Load base model
pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")

# Load LoRA weights
pipe.load_lora_weights("{repo_id}")

# Generate image
prompt = "minimalist tech logo of React, geometric shape, flat design, single color"
image = pipe(prompt, num_inference_steps=50, guidance_scale=12.0).images[0]
image.save("output.png")
```

## Trigger Words

Use these keywords for best results:
- `minimalist tech logo`
- `geometric shape`
- `flat design`
- `single color`

## Example Prompts

- `minimalist tech logo of Python, geometric shape, flat design, single color`
- `minimalist tech logo of GitHub, geometric shape, flat design, single color`
- `minimalist tech logo of Docker, geometric shape, flat design, single color`

## Limitations

This is an early version (v1) with limited training data. Results may vary. A v2 with improved parameters is in development.

## Training Details

Trained using Hugging Face Diffusers library with the following parameters:
- Mixed Precision: BF16
- Optimizer: 8-bit Adam
- Gradient Checkpointing: Enabled
- Scheduler: Constant

## License

This model is released under the same license as SDXL 1.0.
"""

    print("创建 README.md...")
    api.upload_file(
        path_or_fileobj=readme_content.encode(),
        path_in_repo="README.md",
        repo_id=repo_id,
        token=HF_TOKEN
    )
    print("✓ README 上传成功")

    print(f"\n🎉 上传完成！")
    print(f"访问你的模型: https://huggingface.co/{repo_id}")

except Exception as e:
    print(f"\n❌ 上传失败: {e}")
    print("请检查:")
    print("1. Token 是否正确")
    print("2. 文件路径是否存在")
    print("3. 网络连接是否正常")

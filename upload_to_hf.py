"""
上传 LoRA 模型到 Hugging Face
使用方法：python upload_to_hf.py
"""

from huggingface_hub import HfApi, create_repo
import os
from pathlib import Path
from dotenv import load_dotenv

# 从 .env 加载配置
load_dotenv()

# 配置信息
HF_TOKEN = os.getenv('HF_TOKEN')
if not HF_TOKEN:
    HF_TOKEN = input("请输入你的 Hugging Face Token: ").strip()

USERNAME = os.getenv('HF_USERNAME')
if not USERNAME:
    USERNAME = input("请输入你的 Hugging Face 用户名: ").strip()

REPO_NAME = input("请输入仓库名称 [默认: sdxl-simple-icons-lora]: ").strip() or "sdxl-simple-icons-lora"

# LoRA 文件路径（默认使用项目目录）
DEFAULT_PATH = "./pytorch_lora_weights.safetensors"
LORA_PATH = input(f"请输入 LoRA 文件路径 [默认: {DEFAULT_PATH}]: ").strip() or DEFAULT_PATH

# 验证文件是否存在
if not os.path.exists(LORA_PATH):
    print(f"❌ 错误：文件不存在: {LORA_PATH}")
    exit(1)

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

## 🔗 Links

- **Hugging Face Model**: https://huggingface.co/{repo_id}
- **GitHub Repository** (Training code & tools): https://github.com/Octane0411/lora-playground
- **Training Notebook**: [colab_training.ipynb](https://github.com/Octane0411/lora-playground/blob/main/colab_training.ipynb)

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
- Training Time: ~32 minutes (120 steps)
- Final Loss: 5.11e-5

For complete training configuration and code, see the [GitHub repository](https://github.com/Octane0411/lora-playground).

## Known Issues

This is v1 with limited training data (187 samples). The model may:
- Generate overly simple/abstract shapes
- Have limited style variation
- Work best with tech-related prompts

A v2 with improved parameters is in development.

## Development

Want to improve this model or train your own? Check out:
- [Training notebook](https://github.com/Octane0411/lora-playground/blob/main/colab_training.ipynb)
- [Data collection scripts](https://github.com/Octane0411/lora-playground/tree/main/data_collection)
- [Upload guide](https://github.com/Octane0411/lora-playground/blob/main/README_UPLOAD.md)

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

# AISumerCamp_audio_generation_fight – 改进版管线

本项目在原始 baseline 基础上新增了可配置的“生成-后处理-打分-择优”完整管线，支持本地 CPU 开发与云端 GPU 推理。

## 环境
- 本地：Windows 11、conda 环境名称 `tts`、Python 3.11、AMD 显卡（CPU 推理）
- 云端：Ubuntu 22.04、NVIDIA GPU、CUDA 12.1.0（建议 GPU 推理）

建议分别在两端创建同名 conda 环境并安装依赖：

```bash
conda activate tts
pip install -r requirements.txt
```

备注：若仅使用 F5-TTS 与评分模块，可保持 `configs/pipeline.yaml` 中 `use_xtts: false`。

## 目录结构（新增）
- `configs/pipeline.yaml`：管线配置（设备、候选数、打分权重、后处理参数等）
- `src/generate.py`：多候选 TTS 生成（F5-TTS/XTTS）与参考转写
- `src/postprocess.py`：响度归一化、带限 EQ、轻噪声/设备拟真
- `src/score.py`：ASR 转写（Whisper）、声纹相似度（ECAPA），复合评分
- `src/pipeline.py`：编排执行、择优输出、打包结果

## 运行
1. 准备任务文件与参考音频（已内置 `aigc_speech_generation_tasks/`）
2. 可按需修改 `configs/pipeline.yaml`：
   - `runtime.seeds` 控制每条生成的候选个数
   - `scoring.weights` 控制复合评分权重
   - `postprocess` 控制后处理强度
3. 执行：

```bash
conda activate tts
python -m src.pipeline
```

运行结束后输出：
- `result/1.wav ... 200.wav`
- `result/result.csv`
- `result.zip`
- `result/metadata.json`（记录候选与最终选择）

## 云端推理建议
- 将本地已验证的代码与 `configs/pipeline.yaml` 同步至 GPU 服务器
- 设置 `runtime.device: auto`（自动用 GPU）
- 如需启用 XTTS，设 `generators.use_xtts: true`，并保证 TTS 模型首次下载后可复用缓存
- 可开启 `scoring.antispoof.enabled: true` 并集成对应模型（见 `src/score.py` 留空位）

## 常见问题
- 运行慢：将 `scoring.asr.model_size` 设为 `tiny/base/small`，或减少 `runtime.seeds`
- 生成失败：`f5-tts` 初次运行会下载权重，确保网络可达；Windows 下命令行过长时可减少 `extra_args`
- 结果过“干净”：适度提高 `postprocess.add_noise_dbfs`（如 -40 -> -35），保留真实设备感



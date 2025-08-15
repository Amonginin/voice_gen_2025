from __future__ import annotations

import csv
import json
import os
import random
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import yaml
from tqdm import tqdm

from .generate import generate_candidates_for_task
from .postprocess import process_file
from .score import (
    asr_transcribe_text,
    composite_score,
    dummy_antispoof_score,
    speaker_similarity,
)


def load_config(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_tasks(tasks_csv: str) -> pd.DataFrame:
    return pd.read_csv(tasks_csv)


def choose_device(cfg_device: str) -> str:
    if cfg_device == "auto":
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"
    return cfg_device


def process_single_task(task_data: Tuple) -> Tuple[int, str, Dict]:
    """处理单个任务的函数，用于多进程并行"""
    (idx, row, gen_cfg, post_cfg, score_cfg, seeds, tmp_dir, base_dir, sr) = task_data

    utt = int(row["utt"]) if "utt" in row else int(row[0])
    ref_rel = row["reference_speech"]
    text = str(row["text"]).strip()
    ref_path = str(base_dir / "aigc_speech_generation_tasks" / ref_rel)

    # 1) generate candidates
    cand_paths = generate_candidates_for_task(
        gen_cfg=gen_cfg,
        utt_id=utt,
        ref_audio_path=ref_path,
        target_text=text,
        seeds=seeds,
        tmp_dir=tmp_dir,
        asr_cfg=score_cfg.get("asr", {}),
    )

    scored: List[Tuple[str, float, float, float, str]] = []
    # 2) post-process + score each candidate
    for c in cand_paths:
        post_wav = str(Path(tmp_dir) / f"utt{utt}_post_{Path(c).stem}.wav")
        ok = process_file(
            in_wav=c,
            out_wav=post_wav,
            sr=sr,
            lufs_target=(
                post_cfg.get("lufs_target", -22.0)
                if post_cfg.get("enabled", True)
                else None
            ),
            add_noise_dbfs=(
                post_cfg.get("add_noise_dbfs", -35.0)
                if post_cfg.get("enabled", True)
                else None
            ),
            highpass_hz=(
                post_cfg.get("highpass_hz", 150)
                if post_cfg.get("enabled", True)
                else None
            ),
            lowpass_hz=(
                post_cfg.get("lowpass_hz", 8000)
                if post_cfg.get("enabled", True)
                else None
            ),
        )
        if not ok:
            continue

        # score components
        hyp_text = (
            asr_transcribe_text(
                post_wav,
                language=score_cfg.get("asr", {}).get("language", "zh"),
                model_size=score_cfg.get("asr", {}).get("model_size", "small"),
            )
            if score_cfg.get("asr", {}).get("enabled", True)
            else ""
        )
        spk_sim = (
            speaker_similarity(ref_path, post_wav)
            if score_cfg.get("speaker", {}).get("enabled", True)
            else 0.0
        )
        spoof_score = (
            dummy_antispoof_score(post_wav)
            if score_cfg.get("antispoof", {}).get("enabled", False)
            else 0.5
        )
        comp = composite_score(
            ref_text=text,
            hyp_text=hyp_text,
            spk_sim=spk_sim,
            spoof_score=spoof_score,
            weights=score_cfg.get("weights", {}),
        )
        scored.append((post_wav, comp, spk_sim, spoof_score, hyp_text))

    if not scored:
        # fallback: just copy first raw candidate if any
        if cand_paths:
            best_path = cand_paths[0]
        else:
            best_path = None
    else:
        scored.sort(key=lambda x: x[1], reverse=True)
        best_path = scored[0][0]

    metadata = {
        "best_path": best_path,
        "candidates": [p for p in cand_paths],
    }

    return utt, best_path, metadata


def run_pipeline_parallel(cfg_path: str = "configs/pipeline.yaml") -> None:
    cfg = load_config(cfg_path)
    runtime = cfg.get("runtime", {})
    data_cfg = cfg.get("data", {})
    gen_cfg = cfg.get("generators", {})
    post_cfg = cfg.get("postprocess", {})
    score_cfg = cfg.get("scoring", {})
    export_cfg = cfg.get("export", {})

    device = choose_device(runtime.get("device", "auto"))
    sr = int(runtime.get("sample_rate", 16000))
    seeds = list(runtime.get("seeds", [0, 1, 2]))
    output_dir = Path(runtime.get("output_dir", "result"))
    tmp_dir = Path(runtime.get("tmp_dir", ".cache/tmp_audio"))
    max_workers = int(
        runtime.get("max_workers", min(8, os.cpu_count() or 4))
    )  # 新增并行参数

    output_dir.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    tasks_csv = data_cfg.get("tasks_csv")
    base_dir = Path(data_cfg.get("base_dir", "."))
    tasks = read_tasks(tasks_csv)

    synthesized_paths: Dict[int, str] = {}
    metadata: Dict[int, Dict] = {}

    # 准备任务数据
    task_list = []
    for idx, row in tasks.iterrows():
        task_data = (
            idx,
            row,
            gen_cfg,
            post_cfg,
            score_cfg,
            seeds,
            tmp_dir.as_posix(),
            base_dir,
            sr,
        )
        task_list.append(task_data)

    # 并行处理
    print(f"使用 {max_workers} 个进程并行处理 {len(task_list)} 个任务...")
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = {
            executor.submit(process_single_task, task_data): task_data
            for task_data in task_list
        }

        # 收集结果
        for future in tqdm(as_completed(futures), total=len(futures), desc="处理任务"):
            try:
                utt, best_path, task_metadata = future.result()
                if best_path:
                    # 复制最佳结果到输出目录
                    out_wav = (output_dir / f"{utt}.wav").as_posix()
                    shutil.copy(best_path, out_wav)
                    synthesized_paths[utt] = out_wav
                    metadata[utt] = task_metadata
            except Exception as e:
                print(f"任务处理失败: {e}")

    # 4) write result.csv
    tasks = tasks.copy()
    tasks["synthesized_speech"] = [f"{i}.wav" for i in range(1, len(tasks) + 1)]
    tasks.to_csv(output_dir / "result.csv", index=False)

    # 5) export zip
    if export_cfg.get("make_zip", True):
        zip_name = export_cfg.get("zip_name", "result.zip")
        shutil.make_archive(
            base_name=zip_name.replace(".zip", ""), format="zip", root_dir=output_dir
        )

    # 6) save metadata
    with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_pipeline_parallel()

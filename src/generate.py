import os
import random
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .score import asr_transcribe_text


def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def transcribe_ref_text(asr_bin: str, wav_path: str, language: str = "zh") -> str:
    # Simple wrapper using faster-whisper CLI if available; fallback empty
    try:
        cmd = f"{asr_bin} --language {language} --vad_filter True --task transcribe --output_format txt --file {wav_path} | cat"
        out = subprocess.check_output(
            cmd, shell=True, text=True, stderr=subprocess.DEVNULL
        )
        return out.strip()
    except Exception:
        return ""


def f5_tts_generate(
    model: str,
    ref_audio: str,
    gen_text: str,
    out_wav: str,
    hf_endpoint: Optional[str] = None,
    ref_text: str = "",
    extra_args: str = "",
) -> bool:
    env = os.environ.copy()
    if hf_endpoint:
        env["HF_ENDPOINT"] = hf_endpoint
    ref_text_flag = f" --ref_text \"{ref_text}\"" if ref_text else " --ref_text \"\""
    cmd = (
        f"f5-tts_infer-cli --model {model} --ref_audio \"{ref_audio}\"{ref_text_flag} "
        f"--gen_text \"{gen_text}\" {extra_args}"
    )
    try:
        subprocess.check_output(cmd, shell=True, env=env)
        # f5-tts saves to tests/infer_cli_basic.wav by default
        src = Path("tests/infer_cli_basic.wav")
        if src.exists():
            ensure_dir(Path(out_wav).parent)
            shutil.copy(src, out_wav)
            return True
    except subprocess.CalledProcessError:
        return False
    return False


def xtts_generate(
    speaker_wav: str,
    text: str,
    out_wav: str,
    device: str = "cpu",
    seed: Optional[int] = None,
) -> bool:
    try:
        from TTS.api import TTS  # type: ignore

        # model name kept generic; user can cache on GPU server
        model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        tts = TTS(model_name=model_name, progress_bar=False).to(device)
        ensure_dir(Path(out_wav).parent)
        # XTTS supports seed via torch manual_seed upstream; set globally
        if seed is not None:
            import torch

            torch.manual_seed(seed)
        tts.tts_to_file(text=text, speaker_wav=speaker_wav, file_path=out_wav)
        return Path(out_wav).exists()
    except Exception:
        return False


def generate_candidates_for_task(
    gen_cfg: Dict,
    utt_id: int,
    ref_audio_path: str,
    target_text: str,
    seeds: List[int],
    tmp_dir: str,
    asr_cfg: Dict,
) -> List[str]:
    out_paths: List[str] = []
    ensure_dir(tmp_dir)

    ref_text = ""
    if gen_cfg.get("f5_tts", {}).get("ref_text_from_asr", False) and asr_cfg.get(
        "enabled", False
    ):
        # Transcribe the reference audio to use as ref_text for F5-TTS
        ref_text = asr_transcribe_text(
            wav_path=ref_audio_path,
            language=asr_cfg.get("language", "zh"),
            model_size=asr_cfg.get("model_size", "small"),
        )

    def _variant_args(i: int) -> str:
        # Create light variability across candidates using supported F5-TTS flags
        # without relying on an unsupported --seed flag.
        nfe_options = [36, 40, 44, 48]
        cfg_options = [1.0, 1.1, 1.2]
        sway_options = [0.0, 0.2, 0.35]
        speed_options = [1.0, 0.95, 1.05]
        nfe = nfe_options[i % len(nfe_options)]
        cfg = cfg_options[i % len(cfg_options)]
        sway = sway_options[i % len(sway_options)]
        speed = speed_options[i % len(speed_options)]
        return f"--nfe_step {nfe} --cfg_strength {cfg} --sway_sampling_coef {sway} --speed {speed}"

    for idx, seed in enumerate(seeds):
        # Prefer XTTS if enabled, otherwise F5-TTS
        out_wav = str(Path(tmp_dir) / f"utt{utt_id}_seed{seed}.wav")
        ok = False
        if gen_cfg.get("use_xtts", False):
            device = "cuda" if gen_cfg.get("xtts", {}).get("gpu", False) else "cpu"
            ok = xtts_generate(
                ref_audio_path, target_text, out_wav, device=device, seed=seed
            )
        if not ok and gen_cfg.get("use_f5_tts", True):
            var_args = _variant_args(idx)
            extra = gen_cfg["f5_tts"].get("extra_args", "")
            merged_args = (extra + " " + var_args).strip()
            ok = f5_tts_generate(
                model=gen_cfg["f5_tts"]["model"],
                ref_audio=ref_audio_path,
                gen_text=target_text,
                out_wav=out_wav,
                hf_endpoint=gen_cfg["f5_tts"].get("hf_endpoint"),
                ref_text=ref_text,
                extra_args=merged_args,
            )
        if ok:
            out_paths.append(out_wav)
    return out_paths

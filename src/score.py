from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import soundfile as sf


def load_audio_mono(path: str, target_sr: int) -> Tuple[np.ndarray, int]:
    data, sr = sf.read(path, always_2d=False)
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    if sr != target_sr:
        import librosa

        data = librosa.resample(data, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
    return data.astype(np.float32), sr


def asr_transcribe_text(wav_path: str, language: str = "zh", model_size: str = "small") -> str:
    try:
        from faster_whisper import WhisperModel  # type: ignore

        model = WhisperModel(model_size, device="cpu")
        segments, _ = model.transcribe(wav_path, language=language, vad_filter=True)
        text = "".join([seg.text for seg in segments])
        return text.strip()
    except Exception:
        return ""


def cer(ref: str, hyp: str) -> float:
    try:
        from jiwer import cer as jiwer_cer  # type: ignore

        return float(jiwer_cer(ref, hyp))
    except Exception:
        # very rough fallback
        if not ref:
            return 1.0
        import difflib

        sm = difflib.SequenceMatcher(a=ref, b=hyp)
        return 1.0 - sm.ratio()


def speaker_similarity(ref_wav: str, gen_wav: str) -> float:
    try:
        import torch
        from speechbrain.pretrained import EncoderClassifier  # type: ignore

        classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            run_opts={"device": "cpu"},
            savedir=Path(".cache/speechbrain").as_posix(),
        )
        ref_emb = classifier.encode_batch(torch.from_numpy(sf.read(ref_wav)[0]).unsqueeze(0))
        gen_emb = classifier.encode_batch(torch.from_numpy(sf.read(gen_wav)[0]).unsqueeze(0))
        ref_vec = ref_emb.squeeze(0).detach().cpu().numpy()
        gen_vec = gen_emb.squeeze(0).detach().cpu().numpy()
        cos = float(np.dot(ref_vec, gen_vec) / (np.linalg.norm(ref_vec) * np.linalg.norm(gen_vec) + 1e-8))
        return max(0.0, min(1.0, (cos + 1) / 2))  # map [-1,1] -> [0,1]
    except Exception:
        return 0.0


def dummy_antispoof_score(gen_wav: str) -> float:
    # Placeholder: return 0.5 means neutral; integrate AASIST/RawNet2 on GPU server
    return 0.5


def composite_score(
    ref_text: str,
    hyp_text: str,
    spk_sim: float,
    spoof_score: float,
    weights: Dict[str, float],
) -> float:
    asr_ok = 1.0 - cer(ref_text, hyp_text)
    w_spk = float(weights.get("speaker", 0.45))
    w_asr = float(weights.get("asr", 0.35))
    w_anti = float(weights.get("antispoof", 0.20))
    final = w_spk * spk_sim + w_asr * asr_ok + w_anti * (1.0 - spoof_score)
    return float(final)



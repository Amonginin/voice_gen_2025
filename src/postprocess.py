from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf


def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def highpass_filter(waveform: np.ndarray, sr: int, cutoff_hz: int) -> np.ndarray:
    if cutoff_hz is None or cutoff_hz <= 0:
        return waveform
    import librosa

    b = librosa.effects.preemphasis(waveform, coef=0.0)
    # Simple first-order high-pass via FFT masking (lightweight and portable)
    fft = np.fft.rfft(b)
    freqs = np.fft.rfftfreq(b.shape[-1], 1.0 / sr)
    mask = freqs >= cutoff_hz
    fft = fft * mask
    out = np.fft.irfft(fft, n=b.shape[-1])
    return out.astype(np.float32)


def lowpass_filter(waveform: np.ndarray, sr: int, cutoff_hz: int) -> np.ndarray:
    if cutoff_hz is None or cutoff_hz <= 0:
        return waveform
    fft = np.fft.rfft(waveform)
    freqs = np.fft.rfftfreq(waveform.shape[-1], 1.0 / sr)
    mask = freqs <= cutoff_hz
    fft = fft * mask
    out = np.fft.irfft(fft, n=waveform.shape[-1])
    return out.astype(np.float32)


def add_background_noise_dbfs(waveform: np.ndarray, target_dbfs: float) -> np.ndarray:
    if target_dbfs is None:
        return waveform
    if waveform.size == 0:
        return waveform
    rms = np.sqrt(np.mean(np.square(waveform))) + 1e-9
    current_dbfs = 20 * np.log10(rms)
    noise_db = 10 ** ((target_dbfs) / 20.0)
    noise = np.random.normal(0.0, 1.0, size=waveform.shape).astype(np.float32)
    noise = noise / (np.sqrt(np.mean(noise**2)) + 1e-9) * noise_db
    return (waveform + noise).astype(np.float32)


def normalize_lufs(waveform: np.ndarray, sr: int, target_lufs: float) -> np.ndarray:
    import pyloudnorm as pyln

    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(waveform)
    loudness_normalized = pyln.normalize.loudness(waveform, loudness, target_lufs)
    return loudness_normalized.astype(np.float32)


def load_audio(path: str, target_sr: int) -> tuple[np.ndarray, int]:
    data, sr = sf.read(path, always_2d=False)
    if data.ndim > 1:
        data = np.mean(data, axis=1)
    if sr != target_sr:
        import librosa

        data = librosa.resample(data, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
    return data.astype(np.float32), sr


def save_audio_pcm16(path: str, waveform: np.ndarray, sr: int) -> None:
    ensure_dir(Path(path).parent)
    # clip
    waveform = np.clip(waveform, -1.0, 1.0)
    sf.write(path, waveform, sr, subtype="PCM_16")


def process_file(
    in_wav: str,
    out_wav: str,
    sr: int,
    lufs_target: Optional[float] = -22.0,
    add_noise_dbfs: Optional[float] = -35.0,
    highpass_hz: Optional[int] = 150,
    lowpass_hz: Optional[int] = 8000,
) -> bool:
    try:
        wav, _ = load_audio(in_wav, target_sr=sr)
        if highpass_hz:
            wav = highpass_filter(wav, sr, highpass_hz)
        if lowpass_hz:
            wav = lowpass_filter(wav, sr, lowpass_hz)
        if add_noise_dbfs is not None:
            wav = add_background_noise_dbfs(wav, add_noise_dbfs)
        if lufs_target is not None:
            wav = normalize_lufs(wav, sr, lufs_target)
        save_audio_pcm16(out_wav, wav, sr)
        return True
    except Exception:
        return False



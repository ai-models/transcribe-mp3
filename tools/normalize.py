import glob
import os
import shutil
import sys
from pathlib import Path

import pyloudnorm as pyln
import soundfile as sf


from pathlib import Path

def normalize_audio(input_dir, output_dir, peak, loudness_val, sample_rate=48000):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    audio_files = list(input_path.rglob('*.wav'))
    audio_files.extend(input_path.rglob('*.flac'))

    for filepath in audio_files:
        rel_path = filepath.relative_to(input_path)
        output_subdir = output_path / rel_path.parent
        output_subdir.mkdir(parents=True, exist_ok=True)
        target_file = output_subdir / filepath.name

        data, rate = sf.read(filepath)

        pyln.normalize.peak(data, peak)
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(data)
        loudness_normalized_audio = pyln.normalize.loudness(data, loudness, loudness_val)
        sf.write(target_file, data=loudness_normalized_audio, samplerate=sample_rate)

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    peak = float(sys.argv[3])
    loudness = float(sys.argv[4])
    # sample_rate = int(sys.argv[5])
    normalize_audio(input_dir, output_dir, peak, loudness)
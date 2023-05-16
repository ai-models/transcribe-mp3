import os
import shutil
import sys
from pathlib import Path

import pyloudnorm as pyln
import soundfile as sf


def normalize_audio(input_dir, output_dir, peak, loudness_val, sample_rate=48000):
    audio_files = glob.glob(os.path.join(input_dir, "**/*.{wav,flac}"), recursive=True)

    for filepath in audio_files:
        print(filepath)
        output_subdir = os.path.join(output_dir, os.path.relpath(filepath, input_dir))
        os.makedirs(output_subdir, exist_ok=True)
        base = os.path.basename(filepath)
        target_file = os.path.join(output_subdir, base)

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
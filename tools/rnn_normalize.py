import os
import shutil
import sys
from pathlib import Path

import soundfile as sf
import pyloudnorm as pyln

def main(input_dir, output_dir, peak, loudness_val, sample_rate):
    for root, dirs, files in os.walk(input_dir):
        for name in files:
            if name.endswith(".txt"):
                input_path = os.path.join(root, name)
                output_path = os.path.join(output_dir, os.path.relpath(root, input_dir), name)
                output_dirname = os.path.dirname(output_path)
                os.makedirs(output_dirname, exist_ok=True)
                shutil.copyfile(input_path, output_path)

            if not name.endswith("wav") and not name.endswith("flac"):
                continue

            filepath = os.path.join(root, name)
            output_subdir = root.replace(input_dir, output_dir)
            os.makedirs(os.path.join(output_subdir), exist_ok=True)
            base = os.path.basename(filepath)
            tp_s = os.path.join(output_subdir)
            tf_s = os.path.join(output_subdir, base)
            target_path = Path(tp_s)
            target_file = Path(tf_s)

            data, rate = sf.read(filepath)

            peak_normalized_audio = pyln.normalize.peak(data, peak)
            meter = pyln.Meter(rate)
            loudness = meter.integrated_loudness(data)
            loudness_normalized_audio = pyln.normalize.loudness(data, loudness, loudness_val)
            sf.write(target_file, data=loudness_normalized_audio, samplerate=sample_rate)

if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    peak = float(sys.argv[3])
    loudness = float(sys.argv[4])
    sample_rate = int(sys.argv[5])
    main(input_dir, output_dir, peak, loudness, sample_rate)
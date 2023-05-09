import os
import sys
from pathlib import Path

import soundfile as sf
import pyloudnorm as pyln


input_dir = sys.argv[1]
output_dir = sys.argv[2]

for root, dirs, files in os.walk(input_dir):
    for name in files:
        if not name.endswith("wav"):
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

        peak_normalized_audio = pyln.normalize.peak(data, -6.0)
        meter = pyln.Meter(rate)
        loudness = meter.integrated_loudness(data)
        loudness_normalized_audio = pyln.normalize.loudness(data, loudness, -25.0)
        sf.write(target_file, data=loudness_normalized_audio, samplerate=16000)



# import os
# import subprocess
# import sys
# from pathlib import Path
#
# import pyloudnorm as pyln
# import soundfile as sf
#
# input_dir = sys.argv[1]
# output_dir = sys.argv[2]
#
# rnn = '/home/iguana/projects/python/rnnoise/examples/rnnoise_demo'
#
# for root, dirs, files in os.walk(input_dir):
#     for name in files:
#         if not name.endswith("wav"):
#             continue
#
#         filepath = os.path.join(root, name)
#         output_subdir = root.replace(input_dir, output_dir)
#         os.makedirs(os.path.join(output_subdir), exist_ok=True)
#         base = os.path.basename(filepath)
#         tp_s = os.path.join(output_subdir)
#         tf_s = os.path.join(output_subdir, base)
#         target_path = Path(tp_s)
#         target_file = Path(tf_s)
#
#         subprocess.run(["sox", "-G", "-v", "0.8", filepath, "48k.wav", "remix", "-", "rate", "48000"])
#         subprocess.run(["sox", "48k.wav", "-c", "1", "-r", "48000", "-b", "16", "-e", "signed-integer", "-t", "raw",
#                         "temp.raw"])
#         subprocess.run([rnn, "temp.raw", "rnn.raw"])
#         subprocess.run(
#             ["sox", "-G", "-v", "0.8", "-r", "48k", "-b", "16", "-e", "signed-integer", "rnn.raw", "-t", "wav",
#              "rnn.wav"])
#
#         os.makedirs(target_path, exist_ok=True)
#         subprocess.run(["sox", "rnn.wav", str(target_file), "remix", "-", "highpass", "50", "lowpass", "8000", "rate",
#                         "16000"], stdout=subprocess.PIPE)
#         # remove temp files
#         os.remove("48k.wav")
#         os.remove("temp.raw")
#         os.remove("rnn.raw")
#         os.remove("rnn.wav")
#
#         data, rate = sf.read(target_file)
#
#         peak_normalized_audio = pyln.normalize.peak(data, -6.0)
#         meter = pyln.Meter(rate)
#         loudness = meter.integrated_loudness(data)
#         loudness_normalized_audio = pyln.normalize.loudness(data, loudness, -25.0)
#         sf.write(target_file, data=loudness_normalized_audio, samplerate=16000)

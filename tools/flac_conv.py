import os
import shutil
import subprocess
import sys


input_dir = sys.argv[1]
output_dir = sys.argv[2]


for root, dirs, files in os.walk(input_dir):
    for filename in files:
        if filename.endswith(".wav"):
            input_path = os.path.join(root, filename)
            output_path = os.path.join(output_dir, os.path.relpath(root, input_dir), os.path.splitext(filename)[0] + ".flac")
            output_dirname = os.path.dirname(output_path)
            os.makedirs(output_dirname, exist_ok=True)
            subprocess.run(["ffmpeg", "-i", input_path, "-c:a", "flac", "-b:a", "16000", output_path])
        elif filename.endswith(".txt"):
            input_path = os.path.join(root, filename)
            output_path = os.path.join(output_dir, os.path.relpath(root, input_dir), filename)
            output_dirname = os.path.dirname(output_path)
            os.makedirs(output_dirname, exist_ok=True)
            shutil.copyfile(input_path, output_path)

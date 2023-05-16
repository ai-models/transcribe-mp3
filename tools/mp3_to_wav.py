import hashlib
import os
import subprocess
import sys


import os
import subprocess
import hashlib

def convert(input_dir, output_dir, segment_time, output_samplerate='48000'):
    os.makedirs(output_dir, exist_ok=True)

    for mp3_file in os.listdir(input_dir):
        if mp3_file.endswith('.mp3'):
            mp3_path = os.path.join(input_dir, mp3_file)
            print(f"Processing {mp3_path} ...")

            prefix = hashlib.md5(mp3_path.encode()).hexdigest()[:5]
            output_file = os.path.join(output_dir, f"{prefix}.wav")

            if segment_time == 0 or segment_time is None:
                subprocess.run(['ffmpeg', '-i', mp3_path, '-y', '-loglevel', 'quiet', '-ar', output_samplerate, '-ac', '1', '-sample_fmt', 's16', '-c:a', 'pcm_s16le', output_file], check=True)
            else:
                output_template = os.path.join(output_dir, f"{prefix}_%03d.wav")
                subprocess.run(['ffmpeg', '-i', mp3_path, '-y', '-loglevel', 'quiet', '-ar', output_samplerate, '-ac', '1', '-sample_fmt', 's16', '-f', 'segment', '-segment_time', str(segment_time), '-c:a', 'pcm_s16le', output_template], check=True)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python script.py input_dir output_dir segment_time, output_bitrate")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    segment_time = int(sys.argv[3])
    output_samplerate = sys.argv[4]
    convert(input_dir, output_dir, segment_time, output_samplerate)

import os
import subprocess

import requests
from pathlib import Path
import pyloudnorm as pyln
import soundfile as sf

def prepare_vctk(input_folder, output_folder, output_samplerate):
    # Download the vctk-silences file if it doesn't exist
    silences_path = 'tools/vctk-silences.txt'
    if not os.path.exists(silences_path):
        response = requests.get(silences_url)
        with open(silences_path, 'wb') as f:
            f.write(response.content)

    # Read the silences file
    silences = {}
    with open(silences_path, 'r') as f:
        for line in f:
            parts = line.split()
            filename = parts[0]
            start_time = float(parts[1])
            end_time = float(parts[2])
            silences[filename] = (start_time, end_time)

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all FLAC files in the input directory
    for flac_file in Path(input_folder).rglob('*.flac'):
        filename = flac_file.stem
        input_string = '_'.join(filename.split('_')[:2])  # Extract the first two parts of the filename
        if input_string in silences:
            # Read the audio file
            start_time, end_time = silences[input_string]
            input_path = str(flac_file)
            y, sr = sf.read(input_path)

            # Peak normalization
            peak_normalized_audio = pyln.normalize.peak(y, -6.0)

            # Loudness normalization
            meter = pyln.Meter(sr)
            loudness = meter.integrated_loudness(peak_normalized_audio)
            loudness_normalized_audio = pyln.normalize.loudness(peak_normalized_audio, loudness, -25.0)

            # Trim the audio
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            y_trimmed = loudness_normalized_audio[start_sample:end_sample]

            # Save the trimmed and resampled audio to the output directory
            output_path = os.path.join(output_folder, filename + '.flac')
            sf.write(output_path, data=y_trimmed, samplerate=sr)

    for flac_file in Path(output_folder).rglob('*.flac'):
        input_path = str(flac_file)
        output_path = os.path.splitext(input_path)[0] + '_downsampled.flac'

        # Downsample using FFmpeg
        subprocess.run(['ffmpeg', '-i', input_path, '-ar', str(output_samplerate), output_path], check=True)
        os.replace(output_path, input_path)
        print('Downsampled file saved:', output_path)

if __name__ == '__main__':
    # Set the URL for the vctk-silences file
    silences_url = 'https://raw.githubusercontent.com/nii-yamagishilab/vctk-silence-labels/master/vctk-silences.0.92.txt'
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    output_samplerate = sys.argv[3]  # Output sampling rate in Hz
    prepare_vctk(input_folder, output_folder, output_samplerate)
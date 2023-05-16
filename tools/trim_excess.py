import os
import numpy as np
import librosa
import argparse
import json


def trim_excess_audio(audio, sr, text_len, mean_sec_per_char, std_sec_per_char, silence_threshold=-40):
    dB_audio = librosa.core.amplitude_to_db(np.abs(librosa.core.stft(audio)))
    silence_positions = (dB_audio.mean(axis=0) < silence_threshold).nonzero()[0]

    text_audio_duration = text_len * mean_sec_per_char
    allowed_duration_range = (text_audio_duration - std_sec_per_char, text_audio_duration + std_sec_per_char)

    split_position = 0
    for pos in silence_positions:
        audio_duration = pos * sr / np.shape(dB_audio)[1]
        if allowed_duration_range[0] < audio_duration < allowed_duration_range[1]:
            split_position = pos
            break

    if split_position > 0:
        trimmed_audio = audio[: split_position * int(sr / np.shape(dB_audio)[1])]
    else:
        trimmed_audio = audio

    return trimmed_audio


def main(args):
    root_path = args.root_path
    report_path = args.report_path

    with open(os.path.join(report_path, "data.json"), "r") as f:
        report_data = json.load(f)

    high_deviation_files = report_data["high_deviation_files"]
    mean_sec_per_char = report_data["mean_sec_per_char"]
    std_sec_per_char = report_data["std_sec_per_char"]

    trimmed_files_dir = os.path.join(root_path, "trimmed_files")
    os.makedirs(trimmed_files_dir, exist_ok=True)

    for filename, deviation in high_deviation_files:
        audio, sr = librosa.load(filename, sr=None)
        text_len = len([item for item in report_data["word_count"].keys() if item.lower().strip() in filename][0])

        trimmed_audio = trim_excess_audio(audio, sr, text_len, mean_sec_per_char, std_sec_per_char)
        trimmed_filename = os.path.join(trimmed_files_dir, os.path.basename(filename))

        print(f"Trimming {filename} to {trimmed_filename}")
        librosa.output.write_wav(trimmed_filename, trimmed_audio, sr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_path", required=True, type=str, help="Root path of the dataset.")
    parser.add_argument("--report_path", required=True, type=str, help="Report directory path.")
    args = parser.parse_args()

    main(args)

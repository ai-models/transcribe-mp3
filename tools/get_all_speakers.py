import os
import subprocess
import sys

import torch
from pyannote.audio import Audio
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pydub import AudioSegment
from pydub.silence import split_on_silence

from read_config import read_config

pyannote_token = read_config()["hf_key"]


# Pretrained Models
PIPELINE = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=pyannote_token)
OVERLAP_PIPELINE = Pipeline.from_pretrained("pyannote/overlapped-speech-detection", use_auth_token=pyannote_token)
MODEL = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=torch.device("cuda"))

# Audio
AUDIO = Audio(sample_rate=sys.argv[3], mono="downmix")


# Functions
def audio_len(audio_file):
    audio_file = AudioSegment.from_file(audio_file, format="wav")
    return len(audio_file) / 1000


def process_ground_truth(input_path, output_path, output_sample_rate,
                         min_length_seconds, max_length_seconds, min_silence_len,
                         silence_threshold, keep_silence):
    print(f"Processing ground truth: {input_path}...")

    diarization = PIPELINE(input_path)
    track = AudioSegment.from_wav(input_path)
    SEG_C = 0
    match_count = -1

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start_time = turn.start
        end_time = turn.end
        length = end_time - start_time
        if length > min_length_seconds:
            t1 = int(start_time * 1000)
            t2 = int(end_time * 1000)
            seg = track[t1:t2]

            chunks = split_on_silence(seg, min_silence_len, silence_threshold, keep_silence)
            new_chunks = []
            for i, chunk in enumerate(chunks):
                if len(chunk) > max_length_seconds * 1000:
                    print('Resplitting chunk')
                    subchunks = split_on_silence(chunk, min_silence_len, silence_threshold, keep_silence)
                    new_chunks += subchunks
                else:
                    new_chunks.append(chunk)

            for i, chunk in enumerate(new_chunks):
                outfile = f"{speaker}-{SEG_C}-{i}.wav"
                output_file = os.path.join(output_path, outfile)
                chunk.export(output_file, format="wav", parameters=["-ac", "1", "-ar", str(output_sample_rate)])

                if len(chunk) > max_length_seconds * 1000: # or len(chunk) < 800:
                    os.remove(output_file)
                else:
                    print(f"Processing {input_path} - {speaker} - {i}: Chunks: {len(chunk) - 1}")

                    overlap = OVERLAP_PIPELINE(output_file).get_timeline().support()
                    if overlap:
                        print(f"Skipping {output_file} due to overlapping speech.")
                        os.remove(output_file)
                    else:
                        match_count += 1
                        dirname = os.path.basename(os.path.normpath(output_path))
                        print(f"Matching Audio [{output_file}]: {len(chunk)}")
                    SEG_C += 1

    return match_count, output_path


def main(input_dir, output_dir, output_sample_rate, min_length_seconds, max_length_seconds, min_silence_len, silence_threshold, keep_silence):
    if os.path.exists(output_dir):
        subprocess.run(["rm", "-rf", output_dir])
    subprocess.run(["mkdir", "-p", output_dir])
    print(f"Processing {input_dir}...")
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".wav"):
            input_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, os.path.splitext(file_name)[0])
            subprocess.run(["mkdir", "-p", output_path])

            process_ground_truth(input_path, output_path, output_sample_rate, min_length_seconds, max_length_seconds, min_silence_len, silence_threshold, keep_silence)

if __name__ == "__main__":
    # Constants
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    sample_rate = sys.argv[3]
    output_sample_rate = sys.argv[4]
    min_length_seconds = sys.argv[5]
    max_length_seconds = sys.argv[6]
    min_silence_len = sys.argv[7]
    silence_threshold = sys.argv[8]
    keep_silence = sys.argv[9]
    main(input_dir, output_dir, output_sample_rate, min_length_seconds, max_length_seconds, min_silence_len, silence_threshold, keep_silence)

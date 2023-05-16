import os
import subprocess
import sys

import torch
from pyannote.audio import Audio
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.core import Segment
from pydub import AudioSegment
from pydub.silence import split_on_silence
from scipy.spatial.distance import cdist

from read_config import read_config

# Pretrained Models
pyannote_token = read_config()["hf_key"]
PIPELINE = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=pyannote_token)
OVERLAP_PIPELINE = Pipeline.from_pretrained("pyannote/overlapped-speech-detection", use_auth_token=pyannote_token)
MODEL = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=torch.device("cuda"))

# Audio
AUDIO = Audio(sample_rate=sys.argv[5], mono="downmix")


# Functions
def audio_len(audio_file):
    audio_file = AudioSegment.from_file(audio_file, format="wav")
    return len(audio_file) / 1000


def get_embedding(audio_file):
    segment = Segment(0, audio_len(audio_file))
    waveform, sample_rate = AUDIO.crop(audio_file, segment)
    return MODEL(waveform[None])


def extract_speaker_target(speaker_target_embedding, input_path, output_path,
                distance_threshold,  min_length_seconds, max_length_seconds,
                output_sample_rate, min_silence_len, silence_thresh, keep_silence):
    print(f"Processing ground truth: {input_path}...")

    diarization = PIPELINE(input_path)
    track = AudioSegment.from_wav(input_path)
    SEG_C = 0
    match_count = -1

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start_time = turn.start
        end_time = turn.end

        t1 = int(start_time * 1000)
        t2 = int(end_time * 1000)
        seg = track[t1:t2]

        chunks = split_on_silence(seg, min_silence_len, silence_thresh, keep_silence)
        new_chunks = []
        for i, chunk in enumerate(chunks):
            if len(chunk) > max_length_seconds * 1000:
                subchunks = split_on_silence(chunk, min_silence_len, silence_thresh, keep_silence)
                new_chunks += subchunks
            else:
                new_chunks.append(chunk)

        for i, chunk in enumerate(new_chunks):
            outfile = f"{speaker}-{SEG_C}-{i}.wav"
            output_file = os.path.join(output_path, outfile)
            chunk.export(output_file, format="wav", parameters=["-ac", "1", "-ar", str(output_sample_rate)])

            if len(chunk) > max_length_seconds * 1000 or len(chunk) < min_length_seconds * 1000:
                print(f"Skipping {output_file} due to length.")
                os.remove(output_file)
            else:
                distance = cdist(speaker_target_embedding, get_embedding(output_file), metric="cosine")
                print(f"Processing {input_path} - {speaker} - {i}: Chunks: {len(chunk) - 1} - Distance: {distance}")

                if distance <= distance_threshold:
                    overlap = OVERLAP_PIPELINE(output_file).get_timeline().support()
                    if overlap:
                        print(f"Skipping {output_file} due to overlapping speech.")
                        os.remove(output_file)
                    else:
                        match_count += 1
                        dirname = os.path.basename(os.path.normpath(output_path))
                        print(f"Matching Audio [{dirname}]: {match_count}")
                        output_file_name = f"p001_{match_count:05}_mic1.wav"
                        output_file_path = os.path.join(output_path, output_file_name)
                        os.rename(output_file, output_file_path)
                else:
                    os.remove(output_file)
                SEG_C += 1

    return match_count, output_path


def main(input_dir, output_dir, distance_threshold, speaker_target_file, sample_rate_in, output_sample_rate,
         min_length_seconds, max_length_seconds, min_silence_len, silence_threshold, keep_silence):
    if os.path.exists(output_dir):
        subprocess.run(["rm", "-rf", output_dir])
    subprocess.run(["mkdir", "-p", output_dir])

    speaker_target_embedding = get_embedding(speaker_target_file)
    matching_files = []

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".wav"):
            input_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, os.path.splitext(file_name)[0])
            subprocess.run(["mkdir", "-p", output_path])

            match_count, output_path = extract_speaker_target(
                speaker_target_embedding, input_path, output_path,
                distance_threshold,  min_length_seconds, max_length_seconds,
                sample_rate_in, output_sample_rate,
                min_silence_len, silence_thresh, keep_silence)
            if match_count >= 0:
                matching_file = f"p001_{match_count:05}_mic1.wav"
                matching_files.append(os.path.join(output_path, matching_file))


if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    distance_threshold = sys.argv[3]
    speaker_target_file = sys.argv[4]
    sample_rate_in = sys.argv[5]
    output_sample_rate = sys.argv[6]
    min_length_seconds = sys.argv[7]
    max_length_seconds = sys.argv[8]
    min_silence_len = sys.argv[9]
    silence_threshold = sys.argv[10]
    keep_silence = sys.argv[11]
    main(input_dir, output_dir, distance_threshold, speaker_target_file, sample_rate_in, output_sample_rate,
         min_length_seconds, max_length_seconds, min_silence_len, silence_threshold, keep_silence)

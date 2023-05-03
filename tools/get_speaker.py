import os
import sys
import subprocess
from pyannote.audio import Pipeline
from pydub import AudioSegment
from pydub.silence import split_on_silence
import torch
from scipy.spatial.distance import cdist
from pyannote.audio.pipelines.speaker_verification import PretrainedSpeakerEmbedding
from pyannote.audio import Audio
from pyannote.core import Segment
from tools.read_config import read_config

pyannote_token = read_config()["hf_key"]
# Constants
distance_threshold = 0.40
input_dir = sys.argv[1]
output_dir = sys.argv[2]

# Pretrained Models
PIPELINE = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=pyannote_token)
OVERLAP_PIPELINE = Pipeline.from_pretrained("pyannote/overlapped-speech-detection", use_auth_token=pyannote_token)
MODEL = PretrainedSpeakerEmbedding("speechbrain/spkrec-ecapa-voxceleb", device=torch.device("cuda"))

# Audio
AUDIO = Audio(sample_rate=16000, mono="downmix")

# Functions
def audio_len(audio_file):
    audio_file = AudioSegment.from_file(audio_file, format="wav")
    return len(audio_file) / 1000


def get_embedding(audio_file):
    segment = Segment(0, audio_len(audio_file))
    waveform, sample_rate = AUDIO.crop(audio_file, segment)
    return MODEL(waveform[None])


def process_ground_truth(ground_truth_file, input_path, output_path):
    print(f"Processing {input_path}...")
    ground_truth_embedding = get_embedding(ground_truth_file)

    diarization = PIPELINE(input_path)
    track = AudioSegment.from_wav(input_path)
    SEG_C = 0
    match_count = -1

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start_time = turn.start
        end_time = turn.end
        length = end_time - start_time
        if length > 2:
            t1 = int(start_time * 1000)
            t2 = int(end_time * 1000)
            seg = track[t1:t2]
            # get random number between 200 and 300 - variate lengths of output for better training
            # the more input files, the more random the lengths will be
            # rand = 200 + int(os.urandom(1).hex(), 16) % 100 # gpt's wild way to generate random numbers
            chunks = split_on_silence(seg, min_silence_len=300, silence_thresh=-40, keep_silence=300)
            for i, chunk in enumerate(chunks):
                outfile = f"{speaker}-{SEG_C}-{i}.wav"
                output_file = os.path.join(output_path, outfile)
                # todo: maybe don't need to export to file here, just get embedding from chunk
                # todo: could better utilize memory to hold files, disk writing is a lot of time
                # todo: but makes it easier to debug.
                # todo: maybe use multiprocessing queue to speed up the process
                # todo: also, diarization speaker labels could be checked to 'move on'
                chunk.export(output_file, format="wav", parameters=["-ac", "1", "-ar", "16000"])
                distance = cdist(ground_truth_embedding, get_embedding(output_file), metric="cosine")

                if distance <= distance_threshold:
                    overlap = OVERLAP_PIPELINE(output_file).get_timeline().support()
                    if overlap:
                        print(f"Skipping {output_file} due to overlapping speech.")
                        os.remove(output_file)
                    else:
                        match_count += 1
                        # get last part of sub directory name of output_path
                        dirname = os.path.basename(os.path.normpath(output_path))
                        print(f"Matching Audio [{dirname}]: {match_count}")
                        output_file_name = f"p001_{match_count:05}_mic1.wav"
                        output_file_path = os.path.join(output_path, output_file_name)
                        os.rename(output_file, output_file_path)
                else:
                    os.remove(output_file)
                SEG_C += 1

    return match_count, output_path


def main():
    if os.path.exists(output_dir):
        subprocess.run(["rm", "-rf", output_dir])
    subprocess.run(["mkdir", "-p", output_dir])

    ground_truth_file = 'audio/0input/ground-truth-speaker/p001_00020_mic1.wav'

    matching_files = []

    for file_name in os.listdir(input_dir):
        if file_name.endswith(".wav"):
            input_path = os.path.join(input_dir, file_name)
            output_path = os.path.join(output_dir, os.path.splitext(file_name)[0])
            subprocess.run(["mkdir", "-p", output_path])

            match_count, output_path = process_ground_truth(ground_truth_file, input_path, output_path)
            if match_count >= 0:
                matching_file = f"p001_{match_count:05}_mic1.wav"
                matching_files.append(os.path.join(output_path, matching_file))

if __name__ == "__main__":
    main()

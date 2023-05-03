import collections
import os
import sys

import resampy
import webrtcvad
import soundfile


class Frame(object):
    def __init__(self, bytes, duration):
        self.bytes = bytes
        self.duration = duration


def resample_audio(audio, orig_sr, target_sr):
    audio_resampled = resampy.resample(audio, orig_sr, target_sr, filter='kaiser_fast')
    return audio_resampled


def read_wave(path):
    audio, sample_rate = soundfile.read(path, dtype='int16')
    if audio.ndim > 1:
        audio = audio[:, 0]
    if sample_rate != target_sample_rate:
        audio = resample_audio(audio, sample_rate, target_sample_rate)
        sample_rate = target_sample_rate
    return sample_rate, audio.tobytes()


def vad_collector(sample_rate, frame_duration_ms, padding_duration_ms, vad, audio):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    num_window_frames = num_padding_frames * 2 + 1
    ring_buffer = collections.deque(maxlen=num_window_frames)

    triggered = False
    num_frames = []

    for frame in frame_generator(frame_duration_ms, audio, sample_rate):
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        ring_buffer.append((frame, is_speech))

        if not triggered:
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.8 * ring_buffer.maxlen:
                triggered = True
                for f, s in ring_buffer:
                    num_frames.append(f)

        elif len([f for f, speech in ring_buffer if not speech]) > 0.8 * ring_buffer.maxlen:
            triggered = False

    return num_frames


def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], duration)
        offset += n



# Set VAD parameters
frame_duration = 10  # In milliseconds
padding_duration = 200  # In milliseconds
aggressiveness = 0  # VAD mode, an integer between 0 and 3
target_sample_rate = 16000  # Target sample rate after resampling

# Loop through all WAV files in the subdirectories
input_path = sys.argv[1]
for subdir, dirs, files in os.walk(input_path):
    print(f"Processing [{subdir.split('/')[-1]}]")
    for filename in files:
        if filename.endswith('.wav'):
            file_path = os.path.join(subdir, filename)
            orig_sample_rate, audio = read_wave(file_path)

            if orig_sample_rate != target_sample_rate:
                audio = resample_audio(audio, orig_sample_rate, target_sample_rate)

            vad = webrtcvad.Vad(aggressiveness)
            frames = vad_collector(target_sample_rate, frame_duration, padding_duration, vad, audio)

            speech_duration = sum([f.duration for f in frames])
            total_duration = len(audio) / target_sample_rate

            speech_percentage = speech_duration / total_duration

            if speech_percentage < 0.04:  # Adjust this threshold as needed
                print(f"{filename} has less than 1% speech content.")
                # todo: offer to move somewhere else for manual inspection
                # print(f"Removing {file_path}")
                # os.remove(file_path)
                print(f"{filename}: {speech_percentage}")

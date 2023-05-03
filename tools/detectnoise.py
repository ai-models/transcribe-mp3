import webrtcvad
import numpy as np
import soundfile as sf
import os
import glob

# Define the VAD parameters
vad_mode = 3 # Aggressive mode
vad_frame_length = 30 # VAD frame length in ms

# Define the noise level detection function
def measure_noise_level(audio_data, sample_rate):
    audio_data = audio_data.reshape(-1, 2) # Convert to stereo if necessary
    audio_data = audio_data.mean(axis=1) # Convert to mono
    vad = webrtcvad.Vad(vad_mode)
    noise_levels = []
    for start in np.arange(0, len(audio_data), vad_frame_length * sample_rate // 1000):
        end = start + vad_frame_length * sample_rate // 1000
        audio_frame = audio_data[start:end]
        is_speech = vad.is_speech(audio_frame.tobytes(), sample_rate)
        if not is_speech:
            noise_levels.append(max(abs(audio_frame)))
    return max(noise_levels)

# Define the directory to search in
audio_dir = "2speaker-backup"

# Search for .wav files in subdirectories of the given directory
for subdir in os.listdir(audio_dir):
    sub_dir_path = os.path.join(audio_dir, subdir)
    if os.path.isdir(sub_dir_path):
        for audio_file in glob.glob(os.path.join(sub_dir_path, "**/*.wav"), recursive=True):
            # Load the audio file
            audio_data, sample_rate = sf.read(audio_file)
            print(audio_data.shape)

            # Detect speech segments and measure noise levels
            vad = webrtcvad.Vad(vad_mode)
            noise_levels = []
            speech_segments = []
            for start in np.arange(0, len(audio_data), vad_frame_length * sample_rate // 1000):
                end = start + vad_frame_length * sample_rate // 1000
                audio_frame = audio_data[start:end]
                is_speech = vad.is_speech(audio_frame.tobytes(), sample_rate)
                if is_speech:
                    speech_segments.append(audio_frame)
                else:
                    noise_levels.append(measure_noise_level(audio_frame, sample_rate))

            # Print the noise levels and speech segments
            print(f"Noise levels of {audio_file}: {noise_levels}")
            print(f"Number of speech segments in {audio_file}: {len(speech_segments)}")

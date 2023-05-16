import glob
import os
import sys

from df.enhance import enhance, init_df, load_audio, save_audio


import glob
import os

def clean_directory_with_deepfilter(input_dir, output_dir, output_sr):
    # Create the target directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Recursive file matching using glob
    file_patterns = ["**/*.flac", "**/*.wav", "**/*.mp3"]
    audio_files = []
    for pattern in file_patterns:
        audio_files.extend(glob.glob(os.path.join(input_dir, pattern), recursive=True))

    # Iterate over the matched audio files
    for audio_path in audio_files:
        # Get the relative path of the audio file
        rel_path = os.path.relpath(audio_path, input_dir)

        # Create the corresponding output directory structure
        output_subdir = os.path.join(output_dir, os.path.dirname(rel_path))
        os.makedirs(output_subdir, exist_ok=True)

        # Load the audio file
        audio, _ = load_audio(audio_path, sr=df_state.sr())

        # Denoise the audio
        enhanced = enhance(model, df_state, audio)

        # Save the filtered audio to a temporary file
        filename = os.path.basename(audio_path)
        temp_path = os.path.join(output_subdir, f"temp_{filename}")
        save_audio(temp_path, enhanced, df_state.sr())

        # Use ffmpeg to convert the bitrate to the desired output sample rate
        target_path = os.path.join(output_subdir, filename)
        os.system(f"ffmpeg -i {temp_path} -loglevel quiet -ar {output_sr} {target_path}")

        # Remove the temporary file
        os.remove(temp_path)


if __name__ == "__main__":
    # Load default model
    model, df_state, _ = init_df()

    # Set the source and target directories
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    output_sr = sys.argv[3]
    clean_directory_with_deepfilter(input_dir, output_dir, output_sr)

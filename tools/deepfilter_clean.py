import os

from df.enhance import enhance, init_df, load_audio, save_audio


def clean_directory_with_deepfilter(input_dir, output_dir):
    # Create the target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)

    # Iterate over the files in the source directory
    for filename in os.listdir(source_dir):
        if filename.endswith(".flac"):
            # Load the audio file
            audio_path = os.path.join(source_dir, filename)
            audio, _ = load_audio(audio_path, sr=df_state.sr())

            # Denoise the audio
            enhanced = enhance(model, df_state, audio)

            # Save the filtered audio to a temporary file
            temp_path = os.path.join(target_dir, f"temp_{filename}")
            save_audio(temp_path, enhanced, df_state.sr())

            # Use ffmpeg to convert the bitrate to 16000
            target_path = os.path.join(target_dir, filename)
            os.system(f"ffmpeg -i {temp_path} -ar 16000 {target_path}")

            # Remove the temporary file
            os.remove(temp_path)


if __name__ == "__main__":
    # Load default model
    model, df_state, _ = init_df()

    # Set the source and target directories
    source_dir = sys.argv[1]
    target_dir = sys.argv[2]
    clean_directory_with_deepfilter(source_dir, target_dir)

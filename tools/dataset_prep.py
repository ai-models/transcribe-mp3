import glob
import os
import shutil
import sys


def make_vctk_dataset(input_dir, output_dir_wav, output_dir_txt, speaker_id=None):
    # Create target directories if they don't exist
    print(input_dir)

    # Recursively find all txt files in the source directory
    txt_files = glob.glob(os.path.join(input_dir, '**', '*.txt'), recursive=True)

    # Initialize a counter to keep track of the output file names
    counter = 1

    for txt_file in txt_files:
        speaker_id = os.path.basename(os.path.dirname(txt_file))
        speaker_id = speaker_id.replace("SPEAKER_", "S")
        if not speaker_id:
            print(f"Skipping invalid file path: {txt_file}")
            continue

        os.makedirs(os.path.join(output_dir_txt, speaker_id), exist_ok=True)
        os.makedirs(os.path.join(output_dir_wav, speaker_id), exist_ok=True)
        # Check if the TXT file is empty
        if os.path.getsize(txt_file) == 0:
            print(f"Skipping empty txt: {txt_file}")
            continue

        # Find the associated flac file
        flac_file = txt_file.replace('.txt', '.flac')
        if not os.path.isfile(flac_file):
            print(f"Skipping {txt_file} because associated flac file not found")
            continue

        # Get the destination file paths
        prefix = f"{speaker_id}_{str(counter).zfill(4)}"
        dest_txt_file = os.path.join(output_dir_txt, speaker_id, f"{prefix}.txt")
        dest_flac_file = os.path.join(output_dir_wav, speaker_id, f"{prefix}_mic1.flac")

        # Copy the files to the destination directory
        shutil.copy(txt_file, dest_txt_file)
        shutil.copy(flac_file, dest_flac_file)
        # print(f"Copied {txt_file} and {flac_file} to {dest_txt_file} and {dest_flac_file}")

        # Increment the counter
        counter += 1

    # print(txt_files)
    # print(input_dir)
if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir_wav = sys.argv[2]
    output_dir_txt = sys.argv[3]
    speaker_id = sys.argv[4]
    make_vctk_dataset(input_dir, output_dir_wav, output_dir_txt, speaker_id)

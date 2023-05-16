import glob
import os
import shutil


def make_vctk_dataset(source_dir, target_wav, target_txt, speaker_id):
    # Create target directories if they don't exist
    os.makedirs(os.path.join(target_txt, speaker_id), exist_ok=True)
    os.makedirs(os.path.join(target_wav, speaker_id), exist_ok=True)

    # Recursively find all txt files in the source directory
    txt_files = glob.glob(os.path.join(source_dir, '**', '*.txt'), recursive=True)

    # Initialize a counter to keep track of the output file names
    counter = 1

    for txt_file in txt_files:
        # Check if the txt file is empty
        if os.path.getsize(txt_file) == 0:
            print(f"Skipping empty file: {txt_file}")
            continue

        # Find the associated flac file
        flac_file = txt_file.replace('.txt', '.flac')
        if not os.path.isfile(flac_file):
            print(f"Skipping {txt_file} because associated flac file not found")
            continue

        # Check if the flac file is under 20kb
        if os.path.getsize(flac_file) < 20 * 1024:
            print(f"Skipping {txt_file} and {flac_file} because flac file is under 20kb")
            continue

        # Get the destination file paths
        prefix = f"{speaker_id}_{str(counter).zfill(4)}"
        dest_txt_file = os.path.join(target_dir, 'txt', speaker_id, f"{prefix}.txt")
        dest_flac_file = os.path.join(target_dir, 'wav48_silence_trimmed', speaker_id, f"{prefix}_mic1.flac")

        # Copy the files to the destination directory
        shutil.copy(txt_file, dest_txt_file)
        shutil.copy(flac_file, dest_flac_file)
        # print(f"Copied {txt_file} and {flac_file} to {dest_txt_file} and {dest_flac_file}")

        # Increment the counter
        counter += 1


if __name__ == "__main__":
    input_dir = sys.argv[1]
    target_wav = sys.argv[2]
    target_txt = sys.argv[3]
    speaker_id = sys.argv[4]
    make_vctk_dataset(input_dir, target_wav, target_txt, speaker_id)

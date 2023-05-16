import os
import shutil
import sys


def scan_and_delete_empty_files(root_dir):
    files_to_delete = []
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            filepath = os.path.join(subdir, file)

            # Check if the text file is empty or if the FLAC file is under 20kb
            if (file.endswith(".txt") and not open(filepath, 'r').read().strip()) or \
                    (file.endswith(".flac") and os.path.getsize(filepath) < 5 * 1024):

                # Remove the txt and the associated flac file if any
                if file.endswith(".txt"):
                    txt_filepath = filepath
                    flac_filepath = filepath.replace(".txt", ".flac")
                else:
                    txt_filepath = filepath.replace(".flac", ".txt")
                    flac_filepath = filepath

                print(f"Marking file for deletion: {txt_filepath}")
                files_to_delete.append(txt_filepath)
                print(f"Marking associated flac file for deletion: {flac_filepath}")
                files_to_delete.append(flac_filepath)


    # Delete the marked files
    for filepath in files_to_delete:
        print(f"Deleting file: {filepath}")
        os.remove(filepath)


def collect_files(source_dir, target_wav, target_txt):
    index_counter = 1

    print(f"Initial index: {index_counter}")

    all_files = []
    for subdir, dirs, files in os.walk(source_dir):
        for file in files:
            filepath = os.path.join(subdir, file)
            if file.endswith(".txt") or file.endswith(".flac"):
                all_files.append((file, filepath))

    for file1, filepath1 in all_files:
        matched_txt_file = ''
        if file1.endswith(".txt"):
            matched_txt_file = file1
            matched_flac_file = file1.replace(".txt", ".flac")
        elif file1.endswith(".flac"):
            matched_flac_file = file1
            matched_txt_file = file1.replace(".flac", ".txt")
        else:
            continue

        for file2, filepath2 in all_files:
            if file2 == matched_txt_file:
                prefix = f"p001_{str(index_counter).zfill(5)}_mic1"
                destination_flac = os.path.join(target_wav, f"{prefix}.flac")
                destination_txt = os.path.join(target_txt, f"{prefix}.txt").replace("_mic1.txt", ".txt")
                shutil.copy(filepath1, destination_flac)
                shutil.copy(filepath2, destination_txt)
                index_counter += 1
                break



index_counter = 0
def main(root_dir, target_wav, target_txt):
    # Scan and delete empty text files and their associated flac files
    scan_and_delete_empty_files(root_dir)

    # rm -rf target directories
    if os.path.exists(target_wav):
        shutil.rmtree(target_wav)
    if os.path.exists(target_txt):
        shutil.rmtree(target_txt)

    # Make sure directories exist
    os.makedirs(target_wav, exist_ok=True)
    os.makedirs(target_txt, exist_ok=True)

    # Collect files and move them to new directories
    collect_files(root_dir, target_wav, target_txt)

if __name__ == "__main__":
    root_dir = sys.argv[1]
    target_wav = sys.argv[2]
    target_txt = sys.argv[3]

    main(root_dir, target_wav, target_txt)

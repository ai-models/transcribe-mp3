import os
import shutil


def scan_and_delete_empty_files(root_dir):
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            filepath = os.path.join(subdir, file)
            if file.endswith(".txt"):
                with open(filepath, 'r') as f:
                    if not f.read().strip():
                        # Text file is empty
                        os.remove(filepath)
                        print(f"Empty file: {filepath}")
                        # Delete associated flac file if present
                        flac_filepath = filepath.replace(".txt", "_mic1.flac")
                        print(f"Associated flac file: {flac_filepath}")
                        if os.path.exists(flac_filepath):
                            os.remove(flac_filepath)
                        # # stop execution
                        # exit()

def get_highest_index(in_dir, extension):
    highest_index = 0
    for file in os.listdir(in_dir):
        if file.endswith(extension):
            # Extract index value from filename (assuming format: p001_00XXX_mic1.extension)
            index = int(file.split("_")[1])
            if index > highest_index:
                highest_index = index
    return highest_index


def collect_files(source_dir, target_wav, target_txt):
    # Initialize index_counter based on existing files in target directories
    index_counter = max(get_highest_index(target_wav, ".flac"), get_highest_index(target_txt, ".txt")) + 1
    print(f"Initial index: {index_counter}")
    for subdir, dirs, files in os.walk(source_dir):
        file_pairs = []
        for file in files:
            filepath = os.path.join(subdir, file)
            if file.endswith(".flac") or file.endswith(".txt"):
                file_pairs.append((file, filepath))

        file_pairs.sort()  # Ensures flac and txt pairs have matching order
        for file, filepath in file_pairs:
            prefix = f"p001_{str(index_counter).zfill(5)}_mic1"

            if file.endswith(".flac"):
                destination = os.path.join(target_wav, f"{prefix}.flac")
                shutil.copy(filepath, destination)
            elif file.endswith(".txt"):
                destination = os.path.join(target_txt, f"{prefix}.txt")
                destination = destination.replace("_mic1.txt", ".txt")
                shutil.copy(filepath, destination)

            if file_pairs.index(
                    (file, filepath)) % 2 != 0:  # Increment counter after processing a pair of flac and txt files
                index_counter += 1


def main():
    root_dir = "test/wav48_silence_trimmed/p001"
    target_wav = "audio/dataset/wav48_silence_trimmed/p001"
    target_txt = "audio/dataset/txt/p001"

    # Scan and delete empty text files and their associated flac files
    scan_and_delete_empty_files(root_dir)

    # Make sure directories exist
    os.makedirs(target_wav, exist_ok=True)
    os.makedirs(target_txt, exist_ok=True)

    # Collect files and move them to new directories
    collect_files(root_dir, target_wav, target_txt)

if __name__ == "__main__":
    main()

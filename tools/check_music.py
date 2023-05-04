import json
import subprocess
import os
import shutil

PATH_TO_AUDIO_FILE_1 = "audio/2speaker/"  # replace with the path to your audio file

command = ["python3", "tools/demucs_separate.py", '--two-stem=vocals', "-n", 'htdemucs_ft', PATH_TO_AUDIO_FILE_1]
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
track_list = result.stdout
output = json.loads(track_list.replace("'", "\""))

# input_files = [{'track': 'audio/2speaker/test/p001_00003_mic1.wav'}, {'track': 'audio/2speaker/test/p001_00004_mic1.wav'}, {'track': 'audio/2speaker/test/p001_00000_mic1.wav'}]
output_dir = 'audio/2speaker/discarded'

for file_dict in output:
    file_path = file_dict['track']
    subfolder_name = os.path.basename(os.path.dirname(file_path))
    file_name = os.path.basename(file_path)
    new_file_path = os.path.join(output_dir, f"{subfolder_name}_{file_name}")
    os.makedirs(os.path.join(output_dir), exist_ok=True)
    shutil.move(file_path, new_file_path)

print(output)
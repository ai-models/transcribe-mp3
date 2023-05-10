import json
import os
import shutil
import subprocess
import sys

PATH_TO_AUDIO_FILE_1 = sys.argv[1] # replace with the path to your audio file

command = ["python3", "tools/demucs_separate.py", '--two-stems', 'vocals', "-n", 'htdemucs_ft', PATH_TO_AUDIO_FILE_1]
print(command)
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
track_list = result.stdout
print("#########")
print(track_list)
output = json.loads(track_list.replace("'", "\""))

output_dir = 'audio/discarded'

for file_dict in output:
    file_path = file_dict['track']
    subfolder_name = os.path.basename(os.path.dirname(file_path))
    file_name = os.path.basename(file_path)
    new_file_path = os.path.join(output_dir, f"{subfolder_name}_{file_name}")
    os.makedirs(os.path.join(output_dir), exist_ok=True)
    shutil.move(file_path, new_file_path)

print(output)
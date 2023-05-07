import os
import sys
import locale
import re

import whisperx
# from _clean_transcript import handle_whisper

locale.getpreferredencoding = lambda: "UTF-8"

def process_audio_directory(input_path, model):
    for root, dirs, files in os.walk(input_path):
        print(f"Processing {root}...")
        for audio_file_name in files:
            if audio_file_name.endswith('.flac'):
                audio_path = os.path.join(root, audio_file_name)
                result = whisperx.transcribe(model, audio_path, initial_prompt="uh, um, like, you know")
                txt_file_name = os.path.splitext(audio_file_name)[0] + '.txt'
                txt_path = os.path.join(root, txt_file_name)
                # remove _mic1 from the file name
                txt_path = txt_path.replace('_mic1', '')
                with open(txt_path, 'w') as f:
                    # Initialize an empty string to store the concatenated text
                    combined_text = ""

                    # Iterate through the list of segments and extract the "text" value from each
                    for i, segments in enumerate(result['segments']):
                        text = segments['text'].strip().replace('\n', ' ')
                        combined_text += text

                        # Add a space between concatenated segments unconditionally
                        if i < len(result['segments']) - 1:
                            combined_text += ' '

                    # code, response = handle_whisper(combined_text)
                    # combined_text = response
                    f.write(combined_text)
                    # if code == 1:  # If there are non white-listed characters
                    #     f.write(combined_text + ' ')
                    # elif code == 500:  # If string is empty
                    #     print(f'File is empty, deleting {audio_file_name}')


if __name__ == "__main__":
    model_name = 'large-v2'
    model = whisperx.load_model(model_name)

    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    process_audio_directory(input_path, model)

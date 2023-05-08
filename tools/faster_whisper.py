import locale
import os
import sys

from faster_whisper import WhisperModel

locale.getpreferredencoding = lambda: "UTF-8"

def process_audio_directory(input_path, model):
    for root, dirs, files in os.walk(input_path):
        print(f"Processing {root}...")
        for audio_file_name in files:
            if audio_file_name.endswith('.flac'):
                audio_path = os.path.join(root, audio_file_name)
                segments, info = model.transcribe(audio_path, beam_size=5)
                txt_file_name = os.path.splitext(audio_file_name)[0] + '.txt'
                txt_path = os.path.join(root, txt_file_name)
                # remove _mic1 from the file name
                txt_path = txt_path.replace('_mic1', '')
                with open(txt_path, 'w') as f:
                    # Initialize an empty string to store the concatenated text
                    combined_text = ""

                    # Iterate through the list of segments and extract the "text" value from each
                    for i, segment in enumerate(segments):
                        text = segment.text.strip().replace('\n', ' ')
                        combined_text += text

                        # Add a space between concatenated segments unconditionally
                        if i < len(segments) - 1:
                            combined_text += ' '

                    f.write(combined_text)

if __name__ == "__main__":
    model_size = "large-v2"
    device = "cuda"  # change to "cpu" if using CPU
    compute_type = "float16"  # change to "int8_float16" if using INT8
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    process_audio_directory(input_path, model)

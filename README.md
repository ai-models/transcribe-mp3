# dataset-pipeline
MP3 -> Dataset pipeline 

# Audio Processing Pipeline

This Bash script defines a series of functions to process audio files using various Python scripts. The pipeline performs the following operations:

1. **MP3 to WAV Conversion [ffmpeg]**: Converts MP3 files to WAV format. This creates a segmented output so the wav files can be processed in memeory.
2. **Deep Cleaning [deepfilter]**: Cleans the audio using deep filtering techniques. 
3. **Extract Samples [pyannote]**: Extracts audio samples from the segmented WAVs (can target individual speaker with embedding.)
4. **Remove noisy tracks [demucs  & custom script]**: Checks and removes samples with background noise/music.
5. **Transcribe [whisper]**: Transcribes audio to text files. 
6. **Dataset Preparation for Speaker**: Prepares the audio dataset for training a speaker model (VCTK formatted).
7. **Normalization [pyloudnorm]**: Normalizes the audio volume.
8. **FLAC Conversion [ffmpeg]**: Converts audio files to FLAC format.
9. **VCTK Normalization and Trimming [pyloundnorm, soundfile]**: Normalizes and trims VCTK audio files. This is if you are using samples from the original VCTK dataset (and many of the other steps probably don't apply).
10. **Text Cleanup [custom]**: Cleans up the transcript text. (didn't work well for me - there is an update which uses openai, not included yet)
11. **Dataset Report [from Coqui notebook]**: Generates a report on the audio dataset.

To use the pipeline, uncomment the desired function calls at the end of the script and provide the appropriate input and output directories. Each function corresponds to a specific operation.

Note: The pipeline relies on various Python scripts and assumes that the required dependencies (including Python packages and FFmpeg) are properly installed.

Feel free to customize the pipeline according to your requirements. Happy audio processing!



# dataset-pipeline
MP3 -> Dataset pipeline 

# Audio Processing Pipeline

This Bash script defines a series of functions to process audio files using various Python scripts. The pipeline performs the following operations:

1. **MP3 to WAV Conversion**: Converts MP3 files to WAV format. This creates a segmented output so the wav files can be processed in memeory.
2. **Deep Cleaning**: Cleans the audio using deep filtering techniques. Uses deepfilter.
3. **Extract Samples**: Extracts audio samples from the segmented WAVs. Uses pyannote. (can target individual speaker with embedding).
4. **Music Cutting**: Checks and removes samples with background noise/music. Uses custom demucs, and then custom thresholds.
5. **Whisper**: Transcribes audio to text files. 
6. **Dataset Preparation for Speaker**: Prepares the audio dataset for training a speaker model (VCTK formatted).
7. **Normalization**: Normalizes the audio volume.
8. **FLAC Conversion**: Converts audio files to FLAC format.
9. **VCTK Normalization and Trimming**: Normalizes and trims VCTK audio files. This is if you are using samples from the original VCTK dataset (and many of the other steps probably don't apply).
10. **Text Cleanup**: Cleans up the transcript text. (didn't work well for me - there is an update which uses openai, not included yet)
11. **Dataset Report**: Generates a report on the audio dataset.

To use the pipeline, uncomment the desired function calls at the end of the script and provide the appropriate input and output directories. Each function corresponds to a specific operation.

Note: The pipeline relies on various Python scripts and assumes that the required dependencies (including Python packages and FFmpeg) are properly installed.

Feel free to customize the pipeline according to your requirements. Happy audio processing!



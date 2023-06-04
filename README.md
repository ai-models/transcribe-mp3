# dataset-pipeline
MP3 -> Dataset pipeline 

# Audio Processing Pipeline

This Bash script defines a series of functions to process audio files using various Python scripts. The pipeline performs the following operations:

1. **MP3 to WAV Conversion**: Converts MP3 files to WAV format.
2. **Deep Cleaning**: Cleans the audio using deep filtering techniques.
3. **Speaker Identification**: Identifies speakers in the audio (can target individual speaker with embedding).
4. **Music Cutting**: Cuts the music from the audio using Demucs separation and noise removal.
5. **Whisper**: Transcribes audio.
6. **Dataset Preparation for Speaker**: Prepares the audio dataset for training a speaker model.
7. **Normalization**: Normalizes the audio volume.
8. **FLAC Conversion**: Converts audio files to FLAC format.
9. **VCTK Normalization and Trimming**: Normalizes and trims VCTK audio files.
10. **Text Cleanup**: Cleans up the transcript text. (there is an update which uses openai, not included yet)
11. **Dataset Report**: Generates a report on the audio dataset.

To use the pipeline, uncomment the desired function calls at the end of the script and provide the appropriate input and output directories. Each function corresponds to a specific operation.

Note: The pipeline relies on various Python scripts and assumes that the required dependencies (including Python packages and FFmpeg) are properly installed.

Feel free to customize the pipeline according to your requirements. Happy audio processing!



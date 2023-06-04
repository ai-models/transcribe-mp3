#!/bin/bash

function mp3_to_wav {
  input_dir="$1"
  output_dir="$2"
  segment_time="0"
  output_samplerate="48000"
  python3 tools/mp3_to_wav.py "$input_dir" "$output_dir" "$segment_time" "$output_samplerate"
}

function deep_clean {
  input_dir="$1"
  output_dir="$2"
  output_samplerate="48000"
  python3 tools/deepfilter_clean.py "$input_dir" "$output_dir" "$output_samplerate"
}

function get_speaker {
  input_dir="$1"
  output_dir="$2"
#  distance_threshold="0.42"
#  target_speaker="audio/ground_truth.wav"
  sample_rate="48000"
  output_samplerate="48000"
  min_length_seconds="2"
  max_length_seconds="10"
  min_silence_len="400"
  silence_thresh="-40"
  keep_silence="200"
  if [[ -n "$target_speaker" && -n "$distance_threshold" ]]; then
    python3 tools/get_speaker.py "$input_dir" "$output_dir" "$distance_threshold" "$target_speaker" "$sample_rate" "$output_samplerate" "$min_length_seconds" "$max_length_seconds" "$min_silence_len" "$silence_thresh" "$keep_silence"
  else
    python3 tools/get_all_speakers.py "$input_dir" "$output_dir" "$sample_rate" "$output_samplerate" "$min_length_seconds" "$max_length_seconds" "$min_silence_len" "$silence_thresh" "$keep_silence"
  fi
}

function cut_music {
  input_dir="$1"
  noise_bass_peaks_threshold="400"
  noise_treble_peaks_threshold="400"
  python tools/demucs_separate.py --two-stems vocals -n htdemucs_ft "$input_dir"
  python tools/remove_noisy_tracks.py "$noise_bass_peaks_threshold" "$noise_treble_peaks_threshold"
}

function whisper {
  input_dir="$1"
  model_name="large-v2"
  python3 tools/whisper.py "$input_dir" "$model_name"
}

function prep_dataset_speaker {
  input_dir="$1"
  target_wav="audio/dataset/wav48_silence_trimmed"
  target_txt="audio/dataset/txt"
#  speaker_id="p001"
  python3 tools/dataset_prep.py "$input_dir" "$target_wav" "$target_txt" "$speaker_id"
}

function normalize {
  input_dir="$1"
  output_dir="$2"
  peak="-6"
  loudness="-27"
#  sample_rate="16000"
  python3 tools/normalize.py "$input_dir" "$output_dir" "$peak" "$loudness" "$sample_rate"
}


function flac_convert {
  python3 tools/flac_conv.py "$1" "$2"
}

function vctk_normalize_and_trim {
  input_dir='vctk-english/wav48_silence_trimmed/p345'
  output_dir='vctk-english/wav48_silence_trimmed/p345-trimmed'
  output_sample_rate=16000
  python3 tools/vctk_normalize_and_trim.py "$input_dir" "$output_dir" "$output_sample_rate"
}

function text_cleanup {
  python3 tools/_clean_transcript.py "$1"
}

function dataset_report {
  python3 tools/dataset-report.py "$1" "$2"
}

#mp3_to_wav "audio/0input" "audio/1wav"
#get_speaker "audio/1wav" "audio/2speaker"
deep_clean "/media/iguana/8a9bf0f0-ba62-4a8d-879e-d46db7eaa8b3/home/iguana/projects/java/tts-voicetrain/dataset-library/uncleruc/wav48_silence_trimmed/p001" "audio/art-clean"
#normalize "audio/2speaker-deepfilter" "audio/3normalize"
#cut_music "audio/3normalize/"
#whisper "audio/3normalize"
#flac_convert "audio/3normalize" "audio/4flac"
#text_cleanup "audio/4flac"
#prep_dataset_speaker "audio/4flac"
#dataset_report "audio/dataset" "16"

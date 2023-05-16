#!/bin/bash

function split_audio {
  # Splits audio into separated files for easier processing
  input_dir="$1"
  output_dir="$2"
  segment_time="1000"
  output_sample_rate="16000"
  python3 tools/split_audio.py "$input_dir" "$output_dir" "$segment_time" "$output_bitrate"
}

function get_speaker {
  input_dir="$1"
  output_dir="$2"
  distance_threshold="0.42"
  target_speaker="audio/ground_truth.wav"
  sample_rate="16000"
  output_sample_rate="16000"
  min_length_seconds="2"
  max_length_seconds="10"
  min_silence_len="300"
  silence_thresh="-40"
  keep_silence="200"
  if [[ -n "$target_speaker" && -n "$distance_threshold" ]]; then
    python3 tools/get_speaker.py "$input_dir" "$output_dir" "$distance_threshold" "$target_speaker" "$sample_rate" "$output_sample_rate" "$min_length_seconds" "$max_length_seconds" "$min_silence_len" "$silence_thresh" "$keep_silence"
  else
    python3 tools/get_all_speakers.py "$input_dir" "$output_dir" "$sample_rate" "$output_sample_rate" "$min_length_seconds" "$max_length_seconds" "$min_silence_len" "$silence_thresh" "$keep_silence"
  fi
}


function cut_music {
  input_dir="$1"
  noise_bass_peaks_threshold = "400"
  noise_treble_peaks_threshold = "400"
  python tools/demucs_separate.py --two-stems vocals -n htdemucs_ft "$input_dir"
  python tools/remove_noisy_tracks.py "$noise_bass_peaks_threshold" "$noise_treble_peaks_threshold"
}

function whisper {
  input_dir = "$1"
  model_name="large-v2"
  python3 tools/whisper.py "$input_dir" "$model_name"
}

function prep_dataset_speaker {
  input_dir = "$1"
  target_wav = "audio/dataset/wav48_silence_trimmed"
  target_txt = "audio/dataset/txt"
  python3 tools/dataset_prep.py "$input_dir" "$target_wav" "$target_txt"
}

function rnn_normalize {
  input_dir = "$1"
  output_dir = "$2"
  peak = "-6"
  loudness = "-27"
  sample_rate = "16000"
  python3 tools/rnn_normalize.py "$input_dir" "$output_dir" "$peak" "$loudness" "$sample_rate"
}

function deepfilter_clean {
  source_dir = "wav48_silence_trimmed/p001"
  target_dir = "wav48_silence_trimmed/p001-clean"
  python3 tools/deepfilter_clean.py "$source_dir" "$target_dir"
}
function flac_convert {
  python3 tools/flac_conv.py "$1" "$2"
}

function vctk_normalize_and_trim {
  input_dir = 'vctk-english/wav48_silence_trimmed/p345'
  output_dir = 'vctk-english/wav48_silence_trimmed/p345-trimmed'
  output_sample_rate = 16000
  python3 tools/vctk_normalize_and_trim.py "$input_dir" "$output_dir" "$output_sample_rate"
}
function text_cleanup {
  python3 tools/_clean_transcript.py "$1"
}

function dataset_report {
  python3 tools/dataset-report.py "$1" "$2"
}

#split_audio "audio/0input" "audio/1split"
#get_speaker "audio/1split" "audio/2speaker"
#rnn_normalize "audio/2speaker" "audio/3rnn_normalize"
#cut_music "audio/3rnn_normalize/"
#whisper "audio/3rnn_normalize"
#flac_convert "audio/3rnn_normalize" "audio/4flac"
#text_cleanup "audio/4flac"
prep_dataset_speaker "audio/4flac"
#dataset_report "audio/dataset" "16"

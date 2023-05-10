#!/bin/bash

function split_audio {
  input_dir="$1"
  output_dir="$2"
  mkdir -p "$output_dir"
  for mp3 in $input_dir/*.mp3; do
    echo "Processing $mp3 ..."
    prefix=$(echo "$mp3" | md5sum | cut -c -5)
    ffmpeg -i "$mp3" -ar 16000 -ac 1 -sample_fmt s16 -f segment -segment_time 1800 -c:a pcm_s16le "$output_dir/${prefix}_%03d.wav"
  done
}

function get_speaker {
  python3 tools/get_speaker.py "$1" "$2"
}

function cut_music {
  python3 tools/check_music.py "$1" "$2"
}

function whisper {
  python3 tools/whisper.py "$1"
}

function fast_whisper {
  python3 tools/fast_whisper.py "$1"
}

function prep_dataset_speaker {
  python3 tools/prep_dataset_speaker.py "$1"
}

function rnn_normalize {
  python3 tools/rnn_normalize.py "$1" "$2"
}

function flac_convert {
  python3 tools/flac_conv.py "$1" "$2"
}

function text_cleanup {
  python3 tools/_clean_transcript.py "$1"
}

#split_audio "audio/0input" "audio/1split"
#get_speaker "audio/1split" "audio/2speaker"
#rnn_normalize "audio/2speaker" "audio/3rnn_normalize"
cut_music "audio/3rnn_normalize"
#fast_whisper "audio/3rnn_normalize"
#flac_convert "audio/3rnn_normalize" "audio/4flac"
#text_cleanup "audio/4flac"
#prep_dataset_speaker "audio/4flac"



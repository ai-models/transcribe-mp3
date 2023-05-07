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

function rnn_normalize {

  input_dir="$1"
  output_dir="$2"

  for subdir in "$input_dir"/*; do
    if [ -d "$subdir" ]; then
      rnnoise_output_dir="$output_dir/rnnoise/$(basename "$subdir")"
      normalize_output_dir="$output_dir/normalized/$(basename "$subdir")"

      # make output dirs
      mkdir -p "$normalize_output_dir"
      mkdir -p "$rnnoise_output_dir"

      for wav in "$subdir"/*.wav; do
        echo "Processing $wav"
        filename=$(basename -- "$wav")
        filename_no_ext="${filename%.*}"
        ffmpeg -i "$wav" -ar 48000 -ac 1 "$rnnoise_output_dir/$filename_no_ext.wav"
        sox -G -v 0.9 "$rnnoise_output_dir/$filename_no_ext.wav" "$rnnoise_output_dir/48k.wav" remix - rate 48000
        sox "$rnnoise_output_dir/48k.wav" -c 1 -r 48000 -b 16 -e signed-integer -t raw "$rnnoise_output_dir/temp.raw"
        /home/iguana/projects/python/rnnoise/examples/rnnoise_demo "$rnnoise_output_dir/temp.raw" "$rnnoise_output_dir/rnn.raw"
        sox -r 48000 -b 16 -e signed-integer "$rnnoise_output_dir/rnn.raw" -t wav "$rnnoise_output_dir/$filename_no_ext.wav"
        rm "$rnnoise_output_dir/temp.raw"
        rm "$rnnoise_output_dir/rnn.raw"
        rm "$rnnoise_output_dir/48k.wav"
      done

      echo "Finished RNNoise processing on files in $subdir"

      for wav in "$rnnoise_output_dir"/*.wav; do
        filename=$(basename "$wav")
        output_path="$normalize_output_dir/${filename%.*}.flac"
        ffmpeg-normalize "$wav" -c:a flac -f -nt rms -t -25  -o "$output_path" -ar 16000
      done

      echo "Finished normalizing files in $rnnoise_output_dir"

    fi
  done
}

function whisper {
  python3 tools/whisper.py "$1"
}

function prep_dataset_speaker {
  python3 tools/prep_dataset_speaker.py "$1"
}

function rnn_normalize_two {
  python3 tools/rnn_normalize.py
}

#split_audio "audio/0input" "audio/1split"
#get_speaker "audio/1split" "audio/2speaker"
#cut_music "audio/2speaker"
#rnn_normalize_two "audio/2speaker" "audio/3rnn"
#whisper "test/wav48_silence_trimmed"
prep_dataset_speaker "test/wav48_silence_trimmed"

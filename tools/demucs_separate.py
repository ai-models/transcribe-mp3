# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# MIT License
#
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path

import librosa
import scipy.signal
import torch as th
import torchaudio as ta
from demucs.apply import apply_model, BagOfModels
from demucs.audio import AudioFile, convert_audio
from demucs.pretrained import get_model_from_args, add_model_flags, ModelLoadingError
from dora.log import fatal


def count_peaks(x, threshold_db):
    # Convert threshold from dB to amplitude
    threshold = 10 ** (threshold_db / 20)
    # Convert torch tensor to numpy array
    x = x.detach().cpu().numpy().flatten()
    # Compute the peak indices and amplitudes using the find_peaks function
    peaks, _ = scipy.signal.find_peaks(x, height=threshold)
    # Return the number of peaks found
    return len(peaks)

def load_track(track, audio_channels, samplerate):
    errors = {}
    wav = None

    try:
        wav = AudioFile(track).read(
            streams=0,
            samplerate=samplerate,
            channels=audio_channels)
    except FileNotFoundError:
        errors['ffmpeg'] = 'FFmpeg is not installed.'
    except subprocess.CalledProcessError:
        errors['ffmpeg'] = 'FFmpeg could not read the file.'

    if wav is None:
        try:
            wav, sr = ta.load(str(track))
        except RuntimeError as err:
            errors['torchaudio'] = err.args[0]
        else:
            wav = convert_audio(wav, sr, samplerate, audio_channels)

    if wav is None:
        print(f"Could not load file {track}. "
              "Maybe it is not a supported file format? ")
        for backend, error in errors.items():
            print(f"When trying to load using {backend}, got the following error: {error}")
        sys.exit(1)
    return wav


def compute_spectral_centroid(signal, sr):
    return librosa.feature.spectral_centroid(y=signal, sr=sr)[0].mean()


def main():
    parser = argparse.ArgumentParser("demucs.separate",
                                     description="Separate the sources for the given tracks")
    parser.add_argument("tracks", type=Path, help='Path to directory containing tracks')
    add_model_flags(parser)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-o",
                        "--out",
                        type=Path,
                        default=Path("separated"),
                        help="Folder where to put extracted tracks. A subfolder "
                             "with the model name will be created.")
    parser.add_argument("--filename",
                        default="{track}/{stem}.{ext}",
                        help="Set the name of output file. \n"
                             'Use "{track}", "{trackext}", "{stem}", "{ext}" to use '
                             "variables of track name without extension, track extension, "
                             "stem name and default output file extension. \n"
                             'Default is "{track}/{stem}.{ext}".')
    parser.add_argument("-d",
                        "--device",
                        default="cuda" if th.cuda.is_available() else "cpu",
                        help="Device to use, default is cuda if available else cpu")
    parser.add_argument("--shifts",
                        default=1,
                        type=int,
                        help="Number of random shifts for equivariant stabilization."
                             "Increase separation time but improves quality for Demucs. 10 was used "
                             "in the original paper.")
    parser.add_argument("--overlap",
                        default=0.25,
                        type=float,
                        help="Overlap between the splits.")
    split_group = parser.add_mutually_exclusive_group()
    split_group.add_argument("--no-split",
                             action="store_false",
                             dest="split",
                             default=True,
                             help="Doesn't split audio in chunks. "
                                  "This can use large amounts of memory.")
    split_group.add_argument("--segment", type=int,
                             help="Set split size of each chunk. "
                                  "This can help save memory of graphic card. ")
    parser.add_argument("--two-stems",
                        dest="stem", metavar="STEM",
                        help="Only separate audio into {STEM} and no_{STEM}. ")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--int24", action="store_true",
                       help="Save wav output as 24 bits wav.")
    group.add_argument("--float32", action="store_true",
                       help="Save wav output as float32 (2x bigger).")
    parser.add_argument("--clip-mode", default="rescale", choices=["rescale", "clamp"],
                        help="Strategy for avoiding clipping: rescaling entire signal "
                             "if necessary  (rescale) or hard clipping (clamp).")
    parser.add_argument("--mp3", action="store_true",
                        help="Convert the output wavs to mp3.")
    parser.add_argument("--mp3-bitrate",
                        default=320,
                        type=int,
                        help="Bitrate of converted mp3.")
    parser.add_argument("-j", "--jobs",
                        default=0,
                        type=int,
                        help="Number of jobs. This can increase memory usage but will "
                             "be much faster when multiple cores are available.")

    args = parser.parse_args()

    try:
        model = get_model_from_args(args)
    except ModelLoadingError as error:
        fatal(error.args[0])

    if args.segment is not None and args.segment < 8:
        fatal("Segment must greater than 8. ")

    if '..' in args.filename.replace("\\", "/").split("/"):
        fatal('".." must not appear in filename. ')

    if isinstance(model, BagOfModels):
        if args.segment is not None:
            for sub in model.models:
                sub.segment = args.segment
    else:
        if args.segment is not None:
            model.segment = args.segment

    model.cpu()
    model.eval()

    path_parts = str(args.tracks).split(os.path.sep)
    if len(path_parts) == 2:
        wav_files = glob.glob(os.path.join(str(args.tracks), "**", "*.wav"), recursive=True)
    elif len(path_parts) == 3:
        wav_files = glob.glob(os.path.join(str(args.tracks), "*.wav"))
    else:
        print("Invalid path: must be either a directory with subdirectories or a directory with WAV files.")
        return print(f"Found {len(wav_files)} files to separate.")
    if not wav_files:
        print("No WAV files found in the specified directory.")
        return

    # Process and analyze each WAV file
    energy_summary = []
    for wav_file in wav_files:
        track = Path(wav_file)
        wav = load_track(track, model.audio_channels, model.samplerate)
        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()
        sources = apply_model(model, wav[None], device=args.device, shifts=args.shifts,
                              split=args.split, overlap=args.overlap, progress=False,
                              num_workers=args.jobs)[0]

        sources = sources * ref.std() + ref.mean()
        bass_noises_count_peaks = int(count_peaks(sources[1],-40))
        high_noises_count_peaks = int(count_peaks(sources[2],-40))

        energy_summary.append({
            'track': str(track),
            'bass_noises_count_peaks': bass_noises_count_peaks,
            'high_noises_count_peaks': high_noises_count_peaks
        })

    # save energy summary list to a file
    with open('energy_summary_list.json', 'w') as f:
        f.write(str(energy_summary))
    # Print the JSON string to the console
    print(energy_summary)


if __name__ == "__main__":
    main()

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
import json
import os
import sys
from pathlib import Path
import subprocess

import numpy as np
from dora.log import fatal
import torch as th
import torchaudio as ta

from demucs.apply import apply_model, BagOfModels
from demucs.audio import AudioFile, convert_audio, save_audio
from demucs.pretrained import get_model_from_args, add_model_flags, ModelLoadingError

def compute_rms_energy(audio_tensor):
    energy = th.sqrt(th.mean(audio_tensor ** 2))
    return energy.item()

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

    wav_files = glob.glob(os.path.join(str(args.tracks), "**", "*.wav"), recursive=True)

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
                              split=args.split, overlap=args.overlap, progress=True,
                              num_workers=args.jobs)[0]
        sources = sources * ref.std() + ref.mean()

        # Assuming sources[0] contains vocals, and sources[1] contains other noise
        vocal_energy = compute_rms_energy(sources[0])
        noise_energy = compute_rms_energy(sources[1])
        vocal_energy2 = compute_rms_energy(sources[2])
        noise_energy2 = compute_rms_energy(sources[3])
        energy_summary.append((track, vocal_energy, noise_energy, vocal_energy2, noise_energy2))

    # Print the energy summary for all tracks
    # Print the energy summary for all tracks with a difference greater than 0.001
    # print("\nTrack Energy Summary (Difference > 0.001):")
    # print(f"{'Track':<30s} {'0 ':<15s} {'1':<15s} {'2':<15s} {'3':<15s}")
    # for track, vocal_energy, noise_energy, vocal_energy2, noise_energy2 in energy_summary:
    #     difference = abs(noise_energy - vocal_energy2)
    #     if difference > 0.002:
    #         print(f"{str(track):<30s} \t {difference} {vocal_energy:<15.6f} {noise_energy:<15.6f} {vocal_energy2:<15.6f} {noise_energy2:<15.6f}")
    #
    # Initialize an empty list to store the results
    energy_summary_list = []

    # Loop over each track and append its summary to the list
    for track, vocal_energy, noise_energy, vocal_energy2, noise_energy2 in energy_summary:
        # print(track, vocal_energy, noise_energy, vocal_energy2, noise_energy2)
        difference = abs(noise_energy - vocal_energy2)
        if difference > 0.002:
            energy_summary_list.append({
                "track": str(track),
                "difference": difference,
                "vocal_energy": vocal_energy,
                "noise_energy": noise_energy,
                "vocal_energy2": vocal_energy2,
                "noise_energy2": noise_energy2
            })
    # Convert the list to a JSON string
    print(energy_summary_list)


if __name__ == "__main__":
    main()

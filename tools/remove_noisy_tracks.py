import json
import os
import sys

# Load the energy summary list from the file
with open('energy_summary_list.json', 'r') as f:
    data = f.read().replace("'", '"')
    energy_summary_list = json.loads(data)

# Parse the command line arguments for the threshold values
bass_noises = int(sys.argv[1])
high_noises = int(sys.argv[2])

# Filter the list of results based on the thresholds
filtered_results = [result for result in energy_summary_list
                    if bass_noises < result['bass_noises_count_peaks']
                    or high_noises < result['high_noises_count_peaks']
                    ]

# Print the filtered results
for result in filtered_results:
    print(f"Track: {result['track']}, Bass Noise Level: {result['bass_noises_count_peaks']}, High Noise Level: {result['high_noises_count_peaks']}")

## make audio/discarded directory
## copy files to audio/discarded directory

# Make the audio/discarded directory if it doesn't exist
if not os.path.exists('audio/discarded'):
    os.makedirs('audio/discarded')

for result in filtered_results:
    # rename track to "p001_bass_noises_count_peaks_high_noises_count_peaks.mp3"
    os.system(f"mv {result['track']} audio/discarded/p001_{result['bass_noises_count_peaks']}_{result['high_noises_count_peaks']}.mp3")

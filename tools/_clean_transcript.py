import os
import re
import sys

import inflect


def handle_whisper(string):
    # If string is empty
    if not string:
        # Send response to indicate deletion of file
        code = 500
        response = "Response is empty"
        print('##### Response is empty')

        return code, response

    override_cases = {
        'MITD 5.1': "emm-eye-tee-dee five point one",
        '9-11': 'nine eleven',
        'M-I-T-D 5-1': "emm-eye-tee-dee five one",
        '952': 'nine five two',
        '225-5278': 'two two five five two seven eight',
        '952-225-5278': 'nine five two two two five five two seven eight',
        'Artbelt.com': 'art bell dot com'
    }

    for key, value in override_cases.items():
        string = string.replace(key, value)


    # Replace domains with phonetic representation
    string = re.sub(r'(\w+\.)+(com|net|org|gov)', lambda x: x.group().replace('.', ' dot '), string)

    phonetic_mapping = {
        "A": "ayy",
        "B": "bee",
        "C": "see",
        "D": "dee",
        "E": "ee",
        "F": "eff",
        "G": "jee",
        "H": "aitch",
        "I": "eye",
        "J": "jay",
        "K": "kay",
        "L": "el",
        "M": "em",
        "N": "en",
        "O": "oh",
        "P": "pee",
        "Q": "cue",
        "R": "ar",
        "S": "ess",
        "T": "tea",
        "U": "you",
        "V": "vee",
        "W": "double-you",
        "X": "eks",
        "Y": "why",
        "Z": "zee",
    }

    # Replace consecutive capitals with phonetic equivalent and insert a dash
    for match in re.findall(r'[A-Z]{2,}', string):
        new_string = "-".join([phonetic_mapping[char] for char in match])
        string = string.replace(match, new_string)

    # special cases
    special_cases = {
        'ISIS': 'eyesys',
        'III': 'three',
        'ATT': 'ayyteean-tee',
        'IPhone': 'eye-phone',
        'NASA': 'nasa'
    }

    def replace(match):
        word = match.group(0)
        if word in special_cases:
            return special_cases[word]
        else:
            return ' '.join([phonetic_mapping[letter] for letter in word])

    string = re.sub(r'([A-Z]{2,})', replace, string)

    string = string.replace('...', '.')

    # Replace numbers with words using inflect
    p = inflect.engine()
    pattern = r'(?<!-)\b\d+\b(?!-)'
    string_with_numbers_replaced = re.sub(pattern, lambda x: p.number_to_words(x.group()), string)

    # Check if there are numbers in the string
    if any(char.isdigit() for char in string_with_numbers_replaced):
        code = 500
        # print('##### String contains numbers')
        response = "String contains numbers"
        return code, response

    allowed_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\u00af\u00b7\u00df\u00e0\u00e1\u00e2\u00e3\u00e4\u00e6\u00e7\u00e8\u00e9\u00ea\u00eb\u00ec\u00ed\u00ee\u00ef\u00f1\u00f2\u00f3\u00f4\u00f5\u00f6\u00f9\u00fa\u00fb\u00fc\u00ff\u0101\u0105\u0107\u0113\u0119\u011b\u012b\u0131\u0142\u0144\u014d\u0151\u0153\u015b\u016b\u0171\u017a\u017c\u01ce\u01d0\u01d2\u01d4\u0430\u0431\u0432\u0433\u0434\u0435\u0436\u0437\u0438\u0439\u043a\u043b\u043c\u043d\u043e\u043f\u0440\u0441\u0442\u0443\u0444\u0445\u0446\u0447\u0448\u0449\u044a\u044b\u044c\u044d\u044e\u044f\u0451\u0454\u0456\u0457\u0491\u2013!'(),-.:;? "

    # Remove non white-listed characters
    filtered_string = ''.join([c for c in string_with_numbers_replaced if c in allowed_characters])


    # Remove any extra spaces (including newlines, tabs, etc.)
    filtered_string = re.sub(r'\s+', ' ', filtered_string).strip()

    # If the string has changed (due to numbers, domains or non-white-listed characters)
    if string_with_numbers_replaced != filtered_string:
        response = filtered_string
        code = 1
        return code, response

    # If string doesn't have any non-white-listed characters
    code = 1
    response = filtered_string
    return code, response

def load_whisper_files(directory):
    # Iterate through all .txt files in the given directory
    for dirname in os.listdir(directory):
        for filename in os.listdir(directory+'/'+dirname):
            if filename.endswith('.txt'):
                # print(f'Processing {filename}')

                filepath = os.path.join(directory+'/'+dirname, filename)

                # Open the file and read its contents
                with open(filepath, 'r') as f:
                    contents = f.read()

                # Process the contents using the handle_whisper function
                code, response = handle_whisper(contents)

                # print(response)
                # If handle_whisper returns something different, update the file
                # if contents != response:
                print('  contents: '+contents)
                print('  response: '+response)

                if code == 1 and response != contents:
                    with open(filepath, 'w') as f:
                        f.write(response)
                if code == 500:
                    os.remove(filepath)
                    # Remove the corresponding audio file
                    audio_filepath = filepath.replace('.txt', '_mic1.flac')
                    os.remove(audio_filepath)
                    print(f'  ### check {filepath}')
load_whisper_files(sys.argv[1])
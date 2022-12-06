#!/usr/bin/python
import argparse
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from tts_object_builder import TTSObjectBuilder  # noqa

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--front_id', type=str, required=True)
    parser.add_argument('--back_id', type=str, required=True)
    parser.add_argument('--size', type=int, required=True)
    parser.add_argument('--output_file', type=str, required=True)
    args = parser.parse_args()

    result = TTSObjectBuilder.build_deck(
        args.size, args.front_id, args.back_id)
    path = os.path.split(args.output_file)[0]
    if not os.path.exists(path):
        os.makedirs(path)

    with open(args.output_file, 'w+') as stream:
        json.dump(result, stream, indent=4)

    print('Saved result in ' + args.output_file)

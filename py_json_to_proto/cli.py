import argparse
import os
from .convert import convert, Options
import sys


parser = argparse.ArgumentParser()

# parser.add_argument("--convert", help="Converts the given json to Proto")
parser.add_argument("--google_timestamp", help="Add timestamp to imports if in json")
parser.add_argument("--inline", help="unsure...this could use a contribution")
parser.add_argument("--input_file", "-i", help="The input file to convert")
parser.add_argument("--output_file", "-o", help="The location to save the protos")

def get_args() -> argparse.Namespace:
    return parser.parse_args(args=None if sys.argv[1:] else ['--help'])

def main():
    args = get_args()
    data =None

    if not args.input_file or not os.path.exists(args.input_file):
        raise ValueError(f"Invalid input file specified: {args.input_file}")

    if not args.output_file:
        raise ValueError(f"No output file name specified: {args.output_file}")

    with open(args.input_file, 'r') as file:
        data = convert(file.read(), Options(args.inline, args.google_timestamp))

    with open(args.output_file, 'w') as file:
        file.write(str(data))

if __name__ == "__main__":
    main()
import os
import glob
from argparse import ArgumentParser
import sys

parser = ArgumentParser()

parser.add_argument("-d", "--day", dest="day", type=str, help="day")

args = parser.parse_args()

abs_path = os.path.dirname(os.path.realpath(__file__))

if args.day:
    day = args.day
else:
    sys.exit("Please give a day")

output = "./merged_data/" + day + "_merged.txt"

files = glob.glob("DASH-" +day + '/*.txt')
files.sort()

first_line = True

with open(output, 'w+') as outfile:
    outfile.write("Key-sender Key-receiver\n")
    for f in files:
        first_line = True
        with open(f) as infile:
            for line in infile:
                if first_line:
                    first_line = False
                else:
                    outfile.write(line)

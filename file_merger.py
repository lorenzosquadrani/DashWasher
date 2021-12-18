import os
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("-d", "--directory", dest="directory", type=str,
                    help="directory of input and output files")
parser.add_argument("-f", "--filename", dest="filename", type=str,
                    help="output file name")
parser.add_argument("-n", "--nfiles", dest="n_files", type=int,
                    help="number of files", required=True)

args = parser.parse_args()

abs_path = os.path.dirname(os.path.realpath(__file__))

N_files = args.n_files

if args.directory:
    directory = args.directory
else:
    directory = "res/"

if args.filename:
    output = directory + args.filename
else:
    output = directory + "merged.txt"

files = [directory + str(idx).zfill(2) + '.txt' for idx in range(N_files)]

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

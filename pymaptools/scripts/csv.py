import unicodecsv as csv
import argparse
import sys
from functools import partial
from pymaptools.iter import isiterable
from operator import itemgetter
from pymaptools.io import GzipFileType


def parse_args(args=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--fields', nargs='*', default=None)
    ap.add_argument('--input_delimiter', default='\t', help='input delimiter')
    ap.add_argument('--output_delimiter', default=',', help='output delimiter')
    ap.add_argument('--output_header', action='store_true')
    ap.add_argument('--input', type=GzipFileType('r'), default=sys.stdin)
    ap.add_argument('--output', type=GzipFileType('w'), default=sys.stdout)
    namespace = ap.parse_args(args)
    return namespace


def get_indices(header, fields):
    return tuple(header.index(f) for f in fields)


def as_tuple(possible_tuple):
    return possible_tuple if isiterable(possible_tuple) else (possible_tuple,)


def run(args):
    reader = csv.reader(args.input, delimiter=args.input_delimiter)
    writer = csv.writer(args.output, delimiter=args.output_delimiter)
    fields = args.fields
    header = reader.next()
    if fields:
        f = itemgetter(*get_indices(header, fields))
        trans = lambda x: as_tuple(f(x))
    else:
        trans = lambda x: x
    if args.output_header:
        trans_header = trans(header)
        writer.writerow(trans_header)
    for row in reader:
        transformed = trans(row)
        writer.writerow(transformed)


if __name__ == "__main__":
    run(parse_args())

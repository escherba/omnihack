"""
Dumps MySQL tables using `mysqldump` into CSV-compatible format
without locking the table.

Typical usage:

    python src/scripts/dump_table.py --table like_events \\
        --fields id user_id entity_id entity_type ts created_at \\
        > /path/outfile
"""
import errno
import sys
import os
import re
import argparse
import subprocess
import unicodecsv as csv


_RE_ALL = re.compile(ur'^\s*INSERT INTO (\w+) \(([^\(\)]*)\) VALUES \((.*)\);\s*$', re.UNICODE)
_RE_NAME = re.compile(ur'\w+', re.UNICODE)


DELIMITERS = {
    'tab': '\t',
    'comma': ','
}


def parse_args(args=None):

    ap = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__)
    ap.add_argument('--table', type=str, required=True, help='table to use')
    ap.add_argument(
        '--fields', type=str, nargs='*', default=None,
        help='limit to these table fields (default: all)')
    ap.add_argument(
        '--output', type=argparse.FileType('w'), default=sys.stdout,
        help='output file (tab-delimited)')
    ap.add_argument(
        '--charset', type=str, default='utf8', help='default character set')
    ap.add_argument(
        '--no_header', action='store_true', help='do not output header')
    ap.add_argument('--host', type=str, default=os.environ.get('AURORA_HOST_READONLY', 'localhost'))
    ap.add_argument('--port', type=int, default=os.environ.get('AURORA_PORT'))
    ap.add_argument('--user', type=str, default=os.environ.get('AURORA_USER'))
    ap.add_argument('--pwd',  type=str, default=os.environ.get('AURORA_PASS'))
    ap.add_argument('--db',   type=str, default=os.environ.get('AURORA_DB'))
    ap.add_argument('--delimiter', type=str, default='tab', choices=DELIMITERS.keys(),
                    help='Delimiter to use for writing output')
    namespace = ap.parse_args(args)
    return namespace


def unescape_row(row):
    unescaped = []
    for v in row:
        if isinstance(v, basestring):
            unescaped.append(v.replace('\\', ''))
        else:
            unescaped.append(v)
    return unescaped


class NullClass:
    def __str__(self):
        return "NULL"

    def __repr__(self):
        return "NULL"


NULL = NullClass()


def process_input(args, stream):
    delimiter = DELIMITERS[args.delimiter]
    writer = csv.writer(args.output, delimiter=delimiter,
                        escapechar='\\', quoting=csv.QUOTE_NONE)
    fields = args.fields
    for idx, line in enumerate(iter(stream.readline, '')):
        match = _RE_ALL.match(line)
        table, column_sg, value_sg = match.groups()
        values = eval(value_sg)
        columns = _RE_NAME.findall(column_sg)
        assert(len(values) == len(columns))
        if fields is not None:
            record = dict(zip(columns, values))
            columns = fields
            values = [record[c] for c in columns]
        if idx == 0 and not args.no_header:
            writer.writerow(columns)
        writer.writerow(unescape_row(values))


def run(args):
    if not args.db:
        sys.stderr.write("You did not specify database name\n")
        sys.exit(1)

    cmd = """
    mysqldump --quick --compress --extended-insert=false --complete-insert=true
      --single-transaction --skip-lock-tables --default-character-set=%(charset)s
      --skip-add-drop-table --skip-add-locks --skip-comments --skip-triggers
      --skip-quote-names --compact --no-create-info
      %(host)s %(port)s %(user)s %(password)s %(databases)s %(tables)s
    """ % dict(
        charset=args.charset,
        host=('--host=\'%s\'' % args.host if args.host else ''),
        port=('--port=\'%s\'' % args.port if args.port else ''),
        user=('--user=\'%s\'' % args.user if args.user else ''),
        password=('--password=\'%s\'' % args.pwd if args.pwd else ''),
        databases=('--databases=\'%s\'' % args.db if args.db else ''),
        tables=('--tables=\'%s\'' % args.table if args.table else ''))

    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    try:
        process_input(args, proc.stdout)
    except IOError as err:
        proc.kill()
        if err.errno != errno.EPIPE:
            raise
    except KeyboardInterrupt:
        proc.kill()


if __name__ == "__main__":
    run(parse_args())

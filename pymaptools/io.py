import argparse
import re
import json
import collections
import gzip
from pymaptools.utils import hasmethod


HAS_GZ_EXTENSION = ur'.*\.gz$'


def open_gz(fname, mode='r', compresslevel=9):
    """
    Transparent substitute to open() for gzip support
    """
    if re.match(HAS_GZ_EXTENSION, fname) is None:
        return open(fname, mode)
    else:
        return gzip.open(fname, mode + 'b', compresslevel)


def parse_json(line):
    """Safe wrapper around json.loads"""
    try:
        return json.loads(line)
    except Exception:
        return None


class FileReader(collections.Iterator):
    """Read files sequentially and return lines from each

    This is basically a quirky reimplementation of FileInput

    >>> reader = FileReader([[1, 2, 3], [4, 5], [], [6, 7]])
    >>> list(reader)
    [1, 2, 3, 4, 5, 6, 7]
    >>> reader = FileReader([[], []])
    >>> list(reader)
    []
    """
    def __init__(self, files, mode='r', openhook=None):
        self._files = iter(files)
        self._curr_handle = None
        self._openhook = openhook
        self._mode = mode
        self._advance_handle()

    def _advance_handle(self):
        filename = self._files.next()
        if self._openhook is None:
            self._curr_handle = filename \
                if hasmethod(filename, 'next') \
                else iter(filename)
        else:
            curr_handle = self._curr_handle
            if hasmethod(curr_handle, 'close'):
                curr_handle.close()
            self._curr_handle = self._openhook(filename, self._mode)

    def __iter__(self):
        return self

    def parse(self, line):
        """Override this method if you want a custom parser"""
        return line

    def next(self):
        line = None
        while line is None:
            try:
                line = self._curr_handle.next()
            except StopIteration:
                self._advance_handle()
        return self.parse(line)


class JSONLineReader(FileReader):
    """A subclass of FileReader specialized for JSON line input

    >>> reader = JSONLineReader([['{"a":1}', '{invalid'], []])
    >>> list(reader)
    [{u'a': 1}, None]
    """
    def parse(self, line):
        return parse_json(line)


def read_text_resource(fname, ignore_prefix='#', strip_whitespace=True):
    """Read a text resource ignoring comments beginning with pound sign
    :param fname: path
    :type fname: str
    :param ignore_prefix: lines matching this prefix will be skipped
    :type ignore_prefix: str
    :param strip_whitespace: whether to strip whitespace
    :type strip_whitespace: bool
    :rtype: generator
    """
    with open(fname, 'r') as fhandle:
        for line in fhandle:
            stripped = line.strip() if strip_whitespace else line
            if ignore_prefix is None or not stripped.startswith(ignore_prefix):
                yield stripped


class GzipFileType(argparse.FileType):
    """Same as argparse.FileType except works transparently with files
    ending with .gz extension
    """

    def __init__(self, mode='r', bufsize=-1, compresslevel=9,
                 name_pattern=HAS_GZ_EXTENSION):
        super(GzipFileType, self).__init__(mode, bufsize)
        self._compresslevel = compresslevel
        self._name_pattern = re.compile(name_pattern)

    def __call__(self, string):
        if re.match(self._name_pattern, string) is None:
            return super(GzipFileType, self).__call__(string)
        else:
            try:
                return gzip.open(string, self._mode + 'b', self._compresslevel)
            except OSError as err:
                raise argparse.ArgumentTypeError(
                    "can't open '%s': %s" % (string, err))

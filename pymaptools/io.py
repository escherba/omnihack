import argparse
import re
import json
import collections
import gzip
import pickle
import joblib
import codecs
from pymaptools.utils import hasmethod, passthrough_context


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


def write_json_line(handle, obj):
    """write a line encoding a JSON object to a file handle"""
    handle.write(u"{}\n".format(json.dumps(obj)))


class FileReader(collections.Iterator):
    """Read files sequentially and return lines from each

    This is basically a quirky reimplementation of FileInput

    >>> reader = FileReader([[1, 2, 3], [4, 5], [], [6, 7]])
    >>> list(reader)
    [1, 2, 3, 4, 5, 6, 7]
    >>> reader = FileReader([[], []])
    >>> list(reader)
    []
    >>> reader = FileReader([])
    >>> list(reader)
    []
    """
    def __init__(self, files, mode='r', openhook=None):
        self._files = iter(files)
        self._curr_handle = None
        self._curr_filename = None
        self._openhook = openhook
        self._mode = mode
        if files:
            self._advance_handle()

    def _advance_handle(self):
        self._curr_filename = self._files.next()
        if self._openhook is None:
            self._curr_handle = self._curr_filename \
                if hasmethod(self._curr_filename, 'next') \
                else iter(self._curr_filename)
        else:
            curr_handle = self._curr_handle
            if hasmethod(curr_handle, 'close'):
                curr_handle.close()
            self._curr_handle = self._openhook(self._curr_filename, self._mode)

    def __iter__(self):
        return self

    def parse(self, line):
        """Override this method if you want a custom parser"""
        return line

    def next(self):
        line = None
        if self._curr_handle is None:
            raise StopIteration()
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


def read_text_resource(finput, encoding='utf-8', ignore_prefix='#'):
    """Read a text resource ignoring comments beginning with pound sign
    :param finput: path or file handle
    :type finput: str, file
    :param encoding: which encoding to use (default: UTF-8)
    :type encoding: str
    :param ignore_prefix: lines matching this prefix will be skipped
    :type ignore_prefix: str, unicode
    :rtype: generator
    """
    ctx = passthrough_context(codecs.iterdecode(finput, encoding=encoding)) \
        if isinstance(finput, file) \
        else codecs.open(finput, 'r', encoding=encoding)
    with ctx as fhandle:
        for line in fhandle:
            if ignore_prefix is not None:
                line = line.split(ignore_prefix)[0]
            line = line.strip()
            if line:
                yield line


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


class DumperFacade(object):
    """Provides a consistent interface to dumper objects"""

    MODEL_DUMP_TYPES = {
        'pickle': dict(load=pickle.load, dump='_dump_pickle'),
        'joblib': dict(load=joblib.load, dump='_dump_joblib')
    }

    def __init__(self, dumper_type='joblib'):
        dumper_props = self.MODEL_DUMP_TYPES[dumper_type]
        self.load = dumper_props['load']
        self.dump = getattr(self, dumper_props['dump'])

    @classmethod
    def keys(cls):
        return cls.MODEL_DUMP_TYPES.keys()

    @staticmethod
    def _dump_joblib(estimator, fname):
        joblib.dump(estimator, fname, compress=9)

    @staticmethod
    def _dump_pickle(estimator, fname):
        with open(fname, 'wb') as fhandle:
            pickle.dump(estimator, fhandle)

    @staticmethod
    def load(fname):
        pass

    @staticmethod
    def dump(obj, fname):
        pass

import argparse
import re
import json
import collections
import gzip
import bz2
import pickle
import joblib
import codecs
from pymaptools.inspect import hasmethod
from pymaptools.utils import joint_context
from pymaptools.iter import isiterable


SUPPORTED_EXTENSION = re.compile(ur'(\.(?:gz|bz2))$', re.IGNORECASE)


def get_extension(fname, regex=SUPPORTED_EXTENSION, lowercase=True):
    """Return a string containing its extension (if matches pattern)
    """
    match = regex.search(fname)
    if match is None:
        return None
    elif lowercase:
        return match.group().lower()
    else:
        return match.group()


FILEOPEN_FUNCTIONS = {
    '.gz': lambda fname, mode='r', compresslevel=9: gzip.open(fname, mode + 'b', compresslevel),
    '.bz2': lambda fname, mode='r', compresslevel=9: bz2.BZ2File(fname, mode, compresslevel)
}


def open_gz(fname, mode='r', compresslevel=9):
    """Transparent substitute to open() for gzip, bz2 support

    If extension was not found or is not supported, assume it's a plain-text file
    """
    extension = get_extension(fname)
    if extension is None:
        return open(fname, mode)
    else:
        fopen_fun = FILEOPEN_FUNCTIONS[extension]
        return fopen_fun(fname, mode, compresslevel)


def parse_json(line):
    """Safe wrapper around json.loads"""
    try:
        return json.loads(line)
    except ValueError:
        return None


def default_encode_json(obj):
    """Default object encoder to JSON

    Warning: one ought to define one's own decoder for one's own
    object; this method works in many cases but may not be correct.
    """
    return obj.__dict__


def write_json_line(handle, obj, default=default_encode_json, **kwargs):
    """write a line encoding a JSON object to a file handle"""
    handle.write(u"%s\n" % json.dumps(obj, default=default, **kwargs))


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
    ctx = joint_context(codecs.iterdecode(finput, encoding=encoding)) \
        if isiterable(finput) \
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
                 name_pattern=SUPPORTED_EXTENSION):
        super(GzipFileType, self).__init__(mode, bufsize)
        self._compresslevel = compresslevel
        self._name_pattern = name_pattern

    def __call__(self, string):
        extension = get_extension(string, regex=self._name_pattern)
        if extension is None:
            return super(GzipFileType, self).__call__(string)
        else:
            fopen_fun = FILEOPEN_FUNCTIONS[extension]
            try:
                return fopen_fun(string, self._mode, self._compresslevel)
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


class SimplePicklableMixin(object):
    def save_to(self, filename):
        with open_gz(filename, "wb") as fhandle:
            pickle.dump(self, fhandle)

    @classmethod
    def load_from(cls, filename):
        with open_gz(filename, "rb") as fhandle:
            obj = pickle.load(fhandle)
            if not isinstance(obj, cls):
                raise TypeError("Loaded object not of expected type %s", cls.__name__)
            return obj

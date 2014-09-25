import argparse
import re
import gzip


class GzipFileType(argparse.FileType):
    """Same as argparse.FileType except works transparently with files
    ending with .gz extension
    """

    def __init__(self, mode='r', bufsize=-1, compresslevel=9,
                 name_pattern=r'.*\.gz$'):
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

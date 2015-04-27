#!/usr/bin/env python2

import unittest
import tempfile
import shutil
import os
from pymaptools.io import open_gz, read_text_resource, GzipFileType, \
    JSONLineReader


class TestIO(unittest.TestCase):

    def setUp(self):
        self.sample_strings = ["a\n", "#b\n", "c\n"]
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def write_file(self, fname, lines):
        fname = os.path.join(self.tmp_dir, fname)

        with open_gz(fname, mode='w') as fh:
            for line in lines:
                fh.write(line)

        return fname

    def eval_file(self, fname, lines, fun=open_gz):
        self.assertTrue(os.path.exists(fname))
        lines = []
        with fun(fname) as fh:
            for line in fh:
                lines.append(line)
        self.assertListEqual(lines, lines)

    def test_gz(self):
        fname = self.write_file('test.gz', self.sample_strings)
        self.eval_file(fname, self.sample_strings, fun=open_gz)
        self.eval_file(fname, self.sample_strings, fun=GzipFileType())

    def test_bz2(self):
        fname = self.write_file('test.bz2', self.sample_strings)
        self.eval_file(fname, self.sample_strings, fun=open_gz)
        self.eval_file(fname, self.sample_strings, fun=GzipFileType())

    def test_noext(self):
        fname = self.write_file('test', self.sample_strings)
        self.eval_file(fname, self.sample_strings, fun=open_gz)
        self.eval_file(fname, self.sample_strings, fun=GzipFileType())

    def test_read_resource(self):
        fname = self.write_file('test', self.sample_strings)
        lines = list(read_text_resource(fname))
        self.assertListEqual(lines, [s.strip() for s in self.sample_strings if not s.startswith('#')])

    def test_json_line_reader(self):
        reader = JSONLineReader([['{"a":1}', '{invalid'], []])
        out = list(reader)
        self.assertEqual("[{u'a': 1}, None]", str(out))


if __name__ == "__main__":
    unittest.run(verbose=True)

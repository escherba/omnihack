#!/usr/bin/env python2

import unittest
import tempfile
import shutil
import os
from pymaptools.io import open_gz, read_text_resource


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

    def eval_file(self, fname, lines):
        self.assertTrue(os.path.exists(fname))
        lines = []
        with open_gz(fname, mode='r') as fh:
            for line in fh:
                lines.append(line)
        self.assertListEqual(lines, lines)

    def test_gz(self):
        fname = self.write_file('test.gz', self.sample_strings)
        self.eval_file(fname, self.sample_strings)

    def test_bz2(self):
        fname = self.write_file('test.bz2', self.sample_strings)
        self.eval_file(fname, self.sample_strings)

    def test_noext(self):
        fname = self.write_file('test', self.sample_strings)
        self.eval_file(fname, self.sample_strings)

    def test_read_resource(self):
        fname = self.write_file('test', self.sample_strings)
        lines = list(read_text_resource(fname))
        self.assertListEqual(lines, [s.strip() for s in self.sample_strings if not s.startswith('#')])

if __name__ == "__main__":
    unittest.run(verbose=True)

#!/usr/bin/python3

import unittest
import iscpy

from pathlib import Path, PurePath

FILE_EXAMPLE_DHCP = PurePath(
    Path(__file__).absolute().parent,
    'test_data/dhcp/example.named.conf'
    )


class TestCreationFromStrings(unittest.TestCase):

    def setUp(self):
        self.named_file = (
            'include "/home/jcollins/roster-dns-management/test/test_data/rndc.key";'
            'options { pid-file "test_data/named.pid";};\n'
            'controls { inet 127.0.0.1 port 35638 allow{localhost;} keys {rndc-key;};};'
            )
        self.maxDiff = None


class TestParsingFromFile(unittest.TestCase):

    def setUp(self):
        with open(FILE_EXAMPLE_DHCP) as fp:
            self.named_file = fp.read()

        # Set maxDiff to None in order to display differences
        self.maxDiff = None


class TestGenerateFileContent(unittest.TestCase):

    def setUp(self):
        with open(FILE_EXAMPLE_DHCP) as fp:
            self.named_file = fp.read()

        # Set maxDiff to None in order to display differences
        self.maxDiff = None


if __name__ == '__main__':
    unittest.main()

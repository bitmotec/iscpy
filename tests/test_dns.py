#!/usr/bin/python3

# Copyright (c) 2009, Purdue University
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# Neither the name of the Purdue University nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Regression test for iscpy.py

Make sure you are running this against a database that can be destroyed.

DO NOT EVER RUN THIS TEST AGAINST A PRODUCTION DATABASE.
"""

__copyright__ = 'Copyright (C) 2009, Purdue University'
__license__ = 'BSD-3-Clause'
__version__ = '1.8.1'

import unittest
import iscpy

from pathlib import Path, PurePath

FILE_EXAMPLE_DNS = PurePath(
    Path(__file__).absolute().parent,
    'test_data/bind/example.named.conf'
    )


class TestParsingFromFile(unittest.TestCase):

    def setUp(self):
        with open(FILE_EXAMPLE_DNS) as fp:
            self.named_file = fp.read()

        # Set maxDiff to None in order to display differences
        self.maxDiff = None

    def testMakeNamedDict(self):
        self.assertEqual(
            iscpy.dns.MakeNamedDict(self.named_file),
            {
                'acls': {'admin': ['192.168.0.0/16', '192.168.1.2/32', '192.168.1.4/32'],
                         'control-hosts': ['127.0.0.1/32', '192.168.1.3/32']},
                'options': {'include': '"/etc/rndc.key"',
                            'logging': {'category "update-security"':
                                {'"security"': True},
                                'category "queries"': {'"query_logging"': True},
                                'channel "query_logging"':
                                    {'syslog': 'local5', 'severity': 'info'},
                                'category "client"': {'"null"': True},
                                'channel "security"':
                                {'file': '"/var/log/named-security.log" versions 10 size 10m',
                                     'print-time': 'yes'}},
                            'options': {'directory': '"/var/domain"',
                                        'recursion': 'yes',
                                        'allow-query': {'any': True},
                                        'max-cache-size': '512M'},
                            'controls': [{'inet * allow': {'control-hosts': True}},
                                         {'keys': {'rndc-key': True}}]},
                'orphan_zones': {},
                'views':
                    {'authorized': {'zones':
                        {'university.edu':
                            {'type': 'slave',
                             'options': {'masters': {'192.168.11.37': True},
                                         'check-names': 'ignore'},
                             'file': 'test_data/university.db.bak'},
                         'smtp.university.edu':
                            {'type': 'master',
                             'options': {'masters': {'192.168.11.37': True}},
                             'file': 'test_data/test_zone.db'},
                         '.':
                            {'type': 'hint', 'options': {}, 'file': 'named.ca'}},
                        'options': {'allow-recursion': {'network-authorized': True},
                                    'recursion': 'yes',
                                    'match-clients': {'network-authorized': True},
                                    'allow-query-cache': {'network-authorized': True},
                                    'additional-from-cache': 'yes',
                                    'additional-from-auth': 'yes'}},
                     'unauthorized': {'zones':
                        {'0.0.127.in-addr.arpa':
                            {'type': 'slave',
                             'options': {'masters': {'192.168.1.3': True}},
                             'file': 'test_data/university.rev.bak'},
                         '1.210.128.in-addr.arpa':
                            {'type': 'master',
                             'options': {'allow-query':
                                 {'network-unauthorized': True}},
                             'file': 'test_data/test_reverse_zone.db'},
                         '.':
                            {'type': 'hint', 'options': {}, 'file': 'named.ca'}},
                     'options': {'recursion': 'no', 'additional-from-cache': 'no',
                                 'match-clients': {'network-unauthorized': True},
                                 'additional-from-auth': 'no'}}}
            }
            )


class TestGenerateFileContent(unittest.TestCase):

    def setUp(self):
        with open(FILE_EXAMPLE_DNS) as fp:
            self.named_file = fp.read()

        # Set maxDiff to None in order to display differences
        self.maxDiff = None

    def testMakeNamedHeader(self):
        self.assertEqual(
            iscpy.dns.DumpNamedHeader(iscpy.dns.MakeNamedDict(self.named_file)),
            'options { directory "/var/domain";\n'
                      'recursion yes;\n'
                      'allow-query { any; };\n'
                      'max-cache-size 512M; };\n'
            'logging { channel "security" { file "/var/log/named-security.log" '
                                           'versions 10 size 10m;\nprint-time '
                                           'yes; };\n'
                      'channel "query_logging" { syslog local5;\n'
                                                'severity info; };\n'
                      'category "client" { "null"; };\n'
                      'category "update-security" { "security"; };\n'
                      'category "queries" { "query_logging"; }; };\n'
            'controls { inet * allow { control-hosts; } keys { rndc-key; }; };\n'
            'include "/etc/rndc.key";'
            )

    def testMakeZoneViewOptions(self):
        self.assertEqual(
            iscpy.dns.MakeZoneViewOptions(iscpy.dns.MakeNamedDict(self.named_file)),
            {
                'views':
                    {
                        'unauthorized': 'recursion no;\n'
                                        'match-clients { network-unauthorized; };\n'
                                        'additional-from-auth no;\n'
                                        'additional-from-cache no;',
                        'authorized':   'recursion yes;\n'
                                        'match-clients { network-authorized; };\n'
                                        'allow-recursion { network-authorized; };\n'
                                        'allow-query-cache { network-authorized; };\n'
                                        'additional-from-auth yes;\n'
                                        'additional-from-cache yes;'
                    },
                'zones':
                    {
                        '0.0.127.in-addr.arpa': 'masters { 192.168.1.3; };',
                        '1.210.128.in-addr.arpa': 'allow-query { network-unauthorized; };',
                        '.' : '',
                        'university.edu': 'masters { 192.168.11.37; };\n'
                                          'check-names ignore;',
                        'smtp.university.edu': 'masters { 192.168.11.37; };'
                    }
            }
            )


if __name__ == '__main__':
    unittest.main()

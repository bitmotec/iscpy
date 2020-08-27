#!/usr/bin/python3

import unittest
import iscpy

from pathlib import Path, PurePath

FILE_EXAMPLE_DHCP_CONF = PurePath(
    Path(__file__).absolute().parent,
    'test_data/dhcp/example.dhcpd.conf'
    )

FILE_EXAMPLE_DHCP_LEASES = PurePath(
    Path(__file__).absolute().parent,
    'test_data/dhcp/example.dhcpd.leases'
    )


class TestLeaseFileCreationFromStrings(unittest.TestCase):

    def setUp(self):

        self.strTestContent = (
            'authoring-byte-order little-endian;\n'
            '\n'
            'lease 192.168.6.123 {\n'
                'starts 3 2020/04/01 16:37:12;\n'
                'nds 3 2020/04/01 18:37:12;\n'
                'tstp 3 2020/04/01 18:37:12;\n'
                'cltt 3 2020/04/01 16:37:12;\n'
                'binding state free;\n'
                'hardware ethernet 00:00:00:00:00:00;\n'
                r'uid "\377\3424?>\000\002\000\000\253\021#\200F\340$\273(G"' ';\n'
                'set vendor-class-identifier = "d-i";\n'
                '}\n'
            )

        self.maxDiff = None

    def testParse(self):

        lstTarget = [
            'authoring-byte-order little-endian', ';',
            'lease 192.168.6.123', '{',
                'starts 3 2020/04/01 16:37:12', ';',
                'nds 3 2020/04/01 18:37:12', ';',
                'tstp 3 2020/04/01 18:37:12', ';',
                'cltt 3 2020/04/01 16:37:12', ';',
                'binding state free', ';',
                'hardware ethernet 00:00:00:00:00:00', ';',
                r'uid "\377\3424?>\000\002\000\000\253\021#\200F\340$\273(G"', ';',
                'set vendor-class-identifier = "d-i"', ';',
                '}'
            ]

        lstTest = iscpy.Explode(iscpy.ScrubComments(self.strTestContent))

        self.assertEqual(lstTest, lstTarget)


class TestLeaseParsingFromFile(unittest.TestCase):

    def setUp(self):
        with open(FILE_EXAMPLE_DHCP_LEASES) as fp:
            self.strLeaseFileContent = fp.read()

        # Set maxDiff to None in order to display differences
        self.maxDiff = None

    def testParse(self):

        lstTarget = [
            'authoring-byte-order little-endian', ';',
            'lease 192.168.6.123', '{',
                'starts 3 2020/04/01 16:37:12', ';',
                'ends 3 2020/04/01 18:37:12', ';',
                'tstp 3 2020/04/01 18:37:12', ';',
                'cltt 3 2020/04/01 16:37:12', ';',
                'binding state free', ';',
                'hardware ethernet 00:00:00:00:00:00', ';',
                'uid "\\377\\3424?>\\000\\002\\000\\000\\253\\021#\\200F\\340$\\273(G"', ';',
                'set vendor-class-identifier = "d-i"', ';',
                '}',
            'lease 192.168.6.114', '{',
                'starts 1 2020/06/08 15:35:51', ';',
                'ends 1 2020/06/08 16:17:31', ';',
                'tstp 1 2020/06/08 16:17:31', ';',
                'cltt 1 2020/06/08 15:35:51', ';',
                'binding state free', ';',
                'hardware ethernet 00:00:00:00:00:00', ';',
                'uid "\\377\\3424?>\\000\\002\\000\\000\\253\\021\\335n\\000\\354\\341\\376y\\030"', ';',
                '}',
            'lease 192.168.6.107', '{',
                'starts 3 2020/06/17 20:02:18', ';',
                'ends 3 2020/06/17 22:02:18', ';',
                'tstp 3 2020/06/17 22:02:18', ';',
                'cltt 3 2020/06/17 20:02:18', ';',
                'binding state free', ';',
                'hardware ethernet 00:00:00:00:00:00', ';',
                'uid "\\001\\230;\\026\\333&)"', ';',
                'set vendor-class-identifier = "dhcpcd-5.5.6"', ';',
                '}',
            'lease 192.168.6.116', '{',
                'starts 5 2020/06/19 10:29:13', ';',
                'ends 5 2020/06/19 12:29:13', ';',
                'cltt 5 2020/06/19 10:29:13', ';',
                'binding state active', ';',
                'next binding state free', ';',
                'rewind binding state free', ';',
                'hardware ethernet 00:00:00:00:00:00', ';',
                'uid "\\001\\254Wu+\\221\\216"', ';',
                'set vendor-class-identifier = "android-dhcp-10"', ';',
                '}',
            'lease 192.168.6.115', '{',
                'starts 5 2020/06/19 11:23:04', ';',
                'ends 5 2020/06/19 13:23:04', ';',
                'cltt 5 2020/06/19 11:23:04', ';',
                'binding state active', ';',
                'next binding state free', ';',
                'rewind binding state free', ';',
                'hardware ethernet 00:00:00:00:00:00', ';',
                'uid "\\001\\000+gQ\\237j"', ';',
                'set vendor-class-identifier = "MSFT 5.0"', ';',
                'client-hostname "Example Name"', ';',
                '}'
            ]

        lstTest = iscpy.Explode(iscpy.ScrubComments(self.strLeaseFileContent))

        self.assertEqual(lstTest, lstTarget)


class TestLeaseGenerateFileContent(unittest.TestCase):

    def setUp(self):
        with open(FILE_EXAMPLE_DHCP_LEASES) as fp:
            self.strLeaseFileContent = fp.read()

        # Set maxDiff to None in order to display differences
        self.maxDiff = None

    def testMakeISC(self):

        strTraget = (
            'authoring-byte-order little-endian;\n'
            'lease 192.168.6.123 { starts 3 2020/04/01 16:37:12;\n'
            'ends 3 2020/04/01 18:37:12;\n'
            'tstp 3 2020/04/01 18:37:12;\n'
            'cltt 3 2020/04/01 16:37:12;\n'
            'binding state free;\n'
            'hardware ethernet 00:00:00:00:00:00;\n'
            'uid "\\377\\3424?>\\000\\002\\000\\000\\253\\021#\\200F\\340$\\273(G";\n'
            'set vendor-class-identifier = "d-i"; }\n'
            'lease 192.168.6.114 { starts 1 2020/06/08 15:35:51;\n'
            'ends 1 2020/06/08 16:17:31;\n'
            'tstp 1 2020/06/08 16:17:31;\n'
            'cltt 1 2020/06/08 15:35:51;\n'
            'binding state free;\n'
            'hardware ethernet 00:00:00:00:00:00;\n'
            'uid "\\377\\3424?>\\000\\002\\000\\000\\253\\021\\335n\\000\\354\\341\\376y\\030"; }\n'
            )

        dicTest = {
            'authoring-byte-order': 'little-endian',
            'lease 192.168.6.123': {
                'starts': '3 2020/04/01 16:37:12',
                'ends': '3 2020/04/01 18:37:12',
                'tstp': '3 2020/04/01 18:37:12',
                'cltt': '3 2020/04/01 16:37:12',
                'binding': 'state free',
                'hardware':'ethernet 00:00:00:00:00:00',
                'uid': '"\\377\\3424?>\\000\\002\\000\\000\\253\\021#\\200F\\340$\\273(G"',
                'set': 'vendor-class-identifier = "d-i"'
                },
            'lease 192.168.6.114': {
                'starts': '1 2020/06/08 15:35:51',
                'ends': '1 2020/06/08 16:17:31',
                'tstp': '1 2020/06/08 16:17:31',
                'cltt': '1 2020/06/08 15:35:51',
                'binding': 'state free',
                'hardware': 'ethernet 00:00:00:00:00:00',
                'uid': '"\\377\\3424?>\\000\\002\\000\\000\\253\\021\\335n\\000\\354\\341\\376y\\030"'
                }
            }

        strTest = iscpy.MakeISC(dicTest, terminate_curly_brackets=False)

        self.assertEqual(strTest, strTraget)

    def testRecreation(self):

        strBase = iscpy.ScrubComments(self.strLeaseFileContent)
        lstBase = strBase.split('}\n')

        lstTarget = []
        for strPart in lstBase:

            lstSubParts = strPart.split(';\n')
            lstSubParts = [x.strip('\n').replace('\n', ' ') for x in lstSubParts]

            lstTarget.append(';\n'.join(lstSubParts)[:-1])
            # remove empty string from end of list
            # in order to avoid a newline while joining later

        strTarget = ' }\n'.join(lstTarget)

        dicTest = iscpy.ParseISCString(self.strLeaseFileContent)
        strTestFileContent = iscpy.MakeISC(dicTest, terminate_curly_brackets=False)

        self.assertEqual(strTestFileContent, strTarget)


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python

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

__version__ = "1.9.0"

import copy
import pickle


def ParseTokens(char_list):
    """Parses exploded isc named.conf portions.

    Inputs:
      char_list: List of isc file parts

    Outputs:
      dict: fragment or full isc file dict
      Recursive dictionary of isc file, dict values can be of 3 types,
      dict, string and bool. Boolean values are always true. Booleans are false
      if key is absent. Booleans represent situations in isc files such as:
        acl "registered" { 10.1.0/32; 10.1.1:/32;}}

      Example:

      {'stanza1 "new"': 'test_info', 'stanza1 "embedded"': {'acl "registered"':
          {'10.1.0/32': True, '10.1.1/32': True}}}
    """

    index = 0
    dictionary_fragment = {}
    new_char_list = copy.deepcopy(char_list)
    if type(new_char_list) == str:
        return new_char_list
    if type(new_char_list) == dict:
        return new_char_list
    last_open = None
    continuous_line = False
    temp_list = []
    key = 0

    while index < len(new_char_list):
        # print("Line:", new_char_list[index])
        if new_char_list[index] == '{':
            last_open = index
        if new_char_list[index] == ';' and continuous_line:
            dictionary_fragment = temp_list
            temp_list = []
            continuous_line = False
        if new_char_list[index] == ';':
            continuous_line = False
        if (len(new_char_list) > index + 1 \
            and new_char_list[index] == '}' \
            and new_char_list[index + 1] != ';'
            ):
            skip, value = Clip(new_char_list[last_open:])
            temp_list.append({key: copy.deepcopy(ParseTokens(value))})
            continuous_line = True
        if (len(new_char_list) > index + 1 \
            and new_char_list[index + 1] == '{' \
            ):
            key = new_char_list.pop(index)
            skip, dict_value = Clip(new_char_list[index:])
            if continuous_line == True:
                temp_list.append({key: copy.deepcopy(ParseTokens(dict_value))})
            else:
                dictionary_fragment[key] = copy.deepcopy(
                    ParseTokens(dict_value)
                    )
            if (key.startswith('lease') \
                or key.startswith('subnet ') \
                or key.startswith('pool')
                ):
                skip += 2
            index += skip
        else:
            if (len(new_char_list[index].split()) == 1 \
                and '{' not in new_char_list
                ):
                for item in new_char_list:
                    if item in [';']:
                        continue
                    dictionary_fragment[item] = True

            # If there are more than 1 'keywords' at new_char_list[index]
            # ex - "recursion no;"
            elif len(new_char_list[index].split()) >= 2:
                dictionary_fragment[new_char_list[index].split()[0]] = ' '.join(
                    new_char_list[index].split()[1:]
                    )
                index += 1

            # If there is just 1 'keyword' at new_char_list[index]
            # ex "recursion;" (not a valid option, but for example's sake it's fine)
            elif(new_char_list[index] not in ['{', ';', '}']):
                key = new_char_list[index]
                dictionary_fragment[key] = True
                index += 1
            index += 1

    return dictionary_fragment


def Clip(char_list):
    """Clips char_list to individual stanza.

    Inputs:
        char_list: partial of char_list from ParseTokens

    Outputs:
        tuple: (int: skip to char list index, list: shortened char_list)
    """

    assert char_list[0] == '{'
    char_list.pop(0)
    skip = 0
    for index, item in enumerate(char_list):
        if item == '{':
            skip += 1
        elif (item == '}' \
                and skip == 0 \
            ):
            return (index, char_list[:index])
        elif item == '}':
            skip -= 1
    raise Exception("Invalid brackets.")


def Explode(isc_string):
    """Explodes isc file into relevant tokens.

    Inputs:
        isc_string: String of isc file

    Outputs:
        list: list of isc file tokens delimited by brackets and semicolons
            ['stanza1 "new"', '{', 'test_info', ';', '}']
    """

    str_array = []
    temp_string = []
    bInSingleQuote = False
    bInDoubleQuote = False
    for iIndex, char in enumerate(isc_string):
        # Check for single quote
        if bInSingleQuote and char == "'" and isc_string[iIndex -1] != "\\":
            bInSingleQuote = False
            temp_string.append(char)
            continue
        if not bInSingleQuote and not bInDoubleQuote and char == "'":
            # Check if quote is terminated
            iPos, strType = _FindQuote(isc_string[iIndex + 1:], "'")
            if iPos > 0 and strType == "'":
                bInSingleQuote = True
                temp_string.append(char)
                continue
        # Check for double quote
        if bInDoubleQuote and char == '"' and isc_string[iIndex -1] != "\\":
            bInDoubleQuote = False
            temp_string.append(char)
            continue
        if not bInDoubleQuote and not bInSingleQuote and char == '"':
            # Check if quote is terminated
            iPos, strType = _FindQuote(isc_string[iIndex + 1:], '"')
            if iPos > 0 and strType == '"':
                bInDoubleQuote = True
                temp_string.append(char)
                continue
        # Keep quote
        if bInSingleQuote or bInDoubleQuote:
            if char in ['\n']:
                temp_string.append(' ')
                continue
            temp_string.append(char)
            continue
        # Process char
        if char in ['\n']:
            continue
        if char in ['{', '}', ';']:
            if ''.join(temp_string).strip() == '':
                str_array.append(char)
            else:
                str_array.append(''.join(temp_string).strip())
                str_array.append(char)
                temp_string = []
        else:
            temp_string.append(char)
    return str_array


def ScrubComments(isc_string):
    """Clears comments from an isc file

    Inputs:
        isc_string: string of isc file

    Outputs:
        string: string of scrubbed isc file
    """

    isc_list = []
    if isc_string is None:
        return ''
    expanded_comment = False
    for line in isc_string.split('\n'):
        no_comment_line = ""
        # Vet out any inline comments
        if '/*' in line.strip():
            try:
                striped_line = line.strip()
                chars = enumerate(striped_line)
                while True:
                    i, c = next(chars)
                    try:
                        if (c == '/' \
                            and striped_line[i + 1] == '*' \
                            ):
                            expanded_comment = True
                            next(chars) # Skip '*'
                            continue
                        elif (c == '*' \
                                and striped_line[i + 1] == '/' \
                            ):
                            expanded_comment = False
                            next(chars) # Skip '/'
                            continue

                    except IndexError:
                        continue # We are at the end of the line
                    if expanded_comment == True:
                        continue
                    else:
                        no_comment_line += c

            except StopIteration:
                if no_comment_line:
                    isc_list.append(no_comment_line)
                continue

        if expanded_comment == True:
            if '*/' in line.strip():
                expanded_comment = False
                isc_list.append(line.split('*/')[-1])
                continue
            else:
                continue
        if line.strip().startswith(('#', '//')):
            continue
        else:
            strTemp = ""
            iQuoteStart, charQuote = _FindQuote(line)
            if iQuoteStart > 0:
                iPosition = 0
                # Check first appering quote
                while True:
                    iQuoteStart, _ = _FindQuote(line[iPosition:], charQuote)
                    if iQuoteStart >= 0:
                        iQuoteStart += iPosition
                        iQuoteEnd, _ = _FindQuote(line[iQuoteStart+1:], charQuote)
                        iQuoteEnd += iQuoteStart + 1
                        # Split string in front of quote on comment chars
                        lstParts1 = line[iPosition:iQuoteStart].split('#')
                        lstParts2 = lstParts1[0].split('//')
                        if len(strTemp) == 0:
                            strTemp += lstParts2[0].lstrip()
                        else:
                            strTemp += lstParts2[0]
                        if (len(lstParts1) > 1 or len(lstParts2) > 1): # Rest of line is a comment
                            isc_list.append(strTemp)
                            break
                        strTemp += line[iQuoteStart:iQuoteEnd + 1]
                        iPosition = iQuoteEnd + 1

                    # Process string without quote or rest of string behind last quote
                    else:
                        iQuoteStart, charQuote = _FindQuote(line[iPosition:])
                        if iQuoteStart < 0:
                            if len(strTemp) > 0:
                                isc_list.append(strTemp + line[iPosition:].split('#')[0].split('//')[0].rstrip())
                                break
                            isc_list.append(line[iPosition:].split('#')[0].split('//')[0].strip())
                            break
            else:
                isc_list.append(line.split('#')[0].split('//')[0].strip())

    return '\n'.join(isc_list)


def _FindQuote(strLine, charQuote=None):

    # Check for quote starts
    if charQuote is None:
        iQuoteStartSingle = strLine.find("'")
        iQuoteStartDouble = strLine.find('"')
    elif charQuote == "'":
        iQuoteStartSingle = strLine.find("'")
        iQuoteStartDouble = -1
    elif charQuote == '"':
        iQuoteStartSingle = -1
        iQuoteStartDouble = strLine.find('"')

    # Check if char was escaped
    while iQuoteStartSingle > 1:
        if strLine[iQuoteStartSingle-1] == '\\':
            iIndex, strType = _FindQuote(strLine[iQuoteStartSingle+1:], "'")
            if iIndex > -1 and strType == "'":
                iQuoteStartSingle += iIndex
            else:
                iQuoteStartSingle = -1
                break
        break

    while iQuoteStartDouble > 1:
        if strLine[iQuoteStartDouble-1] == '\\':
            iIndex, strType = _FindQuote(strLine[iQuoteStartDouble+1:], '"')
            if iIndex > -1 and strType == '"':
                iQuoteStartDouble += iIndex
            else:
                iQuoteStartDouble = -1
                break
        break

    # Found both
    if iQuoteStartSingle > 0 and iQuoteStartDouble > 0:
        if iQuoteStartSingle < iQuoteStartDouble:
            return iQuoteStartSingle, "'"
        return iQuoteStartDouble, '"'
    # Found single
    if iQuoteStartSingle > -1:
        return iQuoteStartSingle, "'"
    # Found double
    if iQuoteStartDouble > -1:
        return iQuoteStartDouble, '"'
    return -1, None


def MakeISC(isc_dict, terminate=True, terminate_curly_brackets=True, end_with_newline=True):
    """Outputs an isc formatted file string from a dict

    Inputs:
        isc_dict: a recursive dictionary to be turned into an isc file
                  (from ParseTokens)
        terminate: use semicolon to terminate all option lines
        terminate_curly_brakets: use semicolon to terminate curly brackets
                                 (if terminate is true)
        end_with_newline:

    Outputs:
        str: string of isc file without indentation
    """

    if terminate == True:
        terminator = ';'
    else:
        terminator = ''
    if type(isc_dict) == str:
        return isc_dict
    isc_list = []
    for option in isc_dict:
        if type(isc_dict[option]) == bool:
            isc_list.append(f'{option}{terminator}')
        elif (type(isc_dict[option]) == str \
               or type(isc_dict[option]) == str \
               ):
            isc_list.append(f'{option} {isc_dict[option]}{terminator}')
        elif type(isc_dict[option]) == list:
            new_list = []
            for item in isc_dict[option]:
                new_list.append(MakeISC(item, terminate=False, end_with_newline=False))
            new_list[-1] = f'{new_list[-1]}{terminator}'
            if not terminate_curly_brackets:
                isc_list.append(f'{option} {{ {" ".join(new_list)} }}')
                continue
            isc_list.append(f'{option} {{ {" ".join(new_list)} }}{terminator}')
        elif type(isc_dict[option]) == dict:
            strSubDic = MakeISC(isc_dict[option],
                    terminate_curly_brackets=terminate_curly_brackets,
                    end_with_newline=False
                    )
            if not terminate_curly_brackets:
                isc_list.append(f'{option} {{ {strSubDic} }}')
                continue
            isc_list.append(f'{option} {{ {strSubDic} }}{terminator}')
    if end_with_newline:
        return '\n'.join(isc_list) + '\n'
    return '\n'.join(isc_list)


def ParseISCString(isc_string):
    """Makes a dictionary from an ISC file string

    Inputs:
        isc_string: string of isc file

    Outputs:
        dict: dictionary of ISC file representation
    """

    return ParseTokens(Explode(ScrubComments(isc_string)))


def Serialize(isc_string):
    """Makes a pickled byte string of a dict from an ISC file string

    Inputs:
        isc_string: string of an isc file

    Outputs:
        serialized_isc: serialized byte string of isc dict
    """

    return pickle.dumps(ParseISCString(isc_string))


def Deserialize(serialized_byte_string):
    """Makes an iscpy dict from a serliazed ISC dict

    Inputs:
        serialized_byte_string: serialized byte string of isc dict

    Outputs:
        deserialized_isc: unserialized dict of serialized isc dict
    """

    return MakeISC(pickle.loads(serialized_byte_string))


def AddZone(json_zone, isc_dict):
    """Add zone to named config

    Inputs:
        json_zone: Zone definition in json format

    Outputs:
        isc dict with added value
    """

    isc_dict.update(json_zone)
    return isc_dict


def ContentToWrite(isc_dict, num_tab, content, tokens):
    """Print ISC dictionary to specific file

    """

    s = ''
    for key, val in isc_dict.items():
        if key in tokens:
            for _, childval in val.items():
                s = key + ' ' + str(childval) + ';\n'
                content.append(s)
                s = ''
            content.append('\n')
        elif isinstance(val, dict):
            for _ in range (0, num_tab):
                s += "\t"
            s += key + " {\n"
            content.append(s)
            num_tab += 1
            ContentToWrite(val, num_tab, content, tokens)
            if num_tab >= 1:
                num_tab -= 1
            s = ''
            for _ in range (0, num_tab):
                s += "\t"
            s += "};\n"
            content.append(s)
            if num_tab == 0:
                content.append("\n")
            s = ''
        else:
            for _ in range (0, num_tab):
                s += "\t"
            if "True" in str(val):
                s += key + ";\n"
            else:
                s += key + " " + str(val) + ";\n"
            content.append(s)
            s = ''
    if num_tab == 0:
        return content


def WriteToFile(isc_dict, isc_specialkeys, filename):
    """Write out the content of a ISC dictionary

    """

    with open(filename, "w") as f:
        conts = ContentToWrite(isc_dict, 0, [], isc_specialkeys)
        for c in conts:
            f.write(c)

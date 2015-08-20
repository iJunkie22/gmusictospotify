from __future__ import unicode_literals, print_function
__author__ = 'ethan'

import io
import os.path


def isgroup(line_str):
    return len(line_str) > 2 and str(line_str[0] + line_str[-2] + line_str[-1]) == "[]\n"


def pullgroup(line_str):
    return line_str[1:-2]


def join_list(l):
    return ",".join(l) if type(l) == list else l


def split_list(l, s=","):
    assert isinstance(l, str) or isinstance(l, unicode)
    return l.split(s) if s in l else l


class IniFile(object):
    def __init__(self, full_text_str):
        self.f1_cache = io.StringIO(full_text_str)
        self.groups = [["", 0, 0]]
        for line in self.f1_cache:
            if isgroup(line):
                pos = self.f1_cache.tell()
                self.groups[-1][-1] = pos - len(line)
                self.groups.append([pullgroup(line), pos, -1])
        self.groups[-1][-1] = self.f1_cache.tell()
        self.f1_cache.seek(0)

        self.groupdict = {x: (y, z) for x, y, z in self.groups if len(x) > 0}
        self.parsed_dict = {k: self.parse_group(k) for k in self.groupdict.keys()}

    @classmethod
    def from_fp(cls, file_path):
        buf1 = io.StringIO()
        with open(file_path, 'r') as fd1:
            buf1.write(u"%s" % fd1.read())

        full_text = buf1.getvalue()
        buf1.close()
        return IniFile(full_text)

    def read_slice(self, start=0, stop=2):
        self.f1_cache.seek(start)
        output = self.f1_cache.read(stop - start)
        self.f1_cache.seek(0)
        return output

    def read_to_dict(self, input_str):
        assert isinstance(input_str, str) or isinstance(input_str, unicode)
        lines = [line.partition("=") for line in input_str.splitlines()]
        kv_pairs = [(k, split_list(v)) for (k, s, v) in lines if s != '']
        return dict(kv_pairs)

    def parse_group(self, group_name):
        g_start, g_stop = self.groupdict[group_name]
        group_slice = self.read_slice(g_start, g_stop)
        return self.read_to_dict(group_slice)

    def group_to_string(self, ini_group):
        return "\n".join(["=".join([k, join_list(v)]) for (k, v) in ini_group.items()])

    def file_to_string(self):
        print("\n".join([("[" + k + "]\n" + self.group_to_string(v) + "\n\n")for k, v in self.parsed_dict.items()]))

cred_fp = os.path.join(os.path.dirname(__file__), 'credentials.ini')

CREDENTIALS = IniFile.from_fp(cred_fp).parsed_dict

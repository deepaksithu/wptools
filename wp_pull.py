#!/usr/bin/env python
"""
Pull article from Wikipedia XML Dump

INPUT
    title   article title
    dump    XML Dump bzip2 file
    -index  index bzip2 file (optional)


OUTPUT
    article wikitext

See also
    wp_parser
    wp_index
"""

from __future__ import print_function

__author__ = "siznax"
__version__ = "30 Sep 2015"

import argparse
import bz2
import re
import sys
import time

from wp_parser import WPParser
from wp_index import page_title

CHUNK_SIZE = 1024


class PullParser(WPParser):

    def __init__(self, title):
        WPParser.__init__(self)
        self.title = title
        self.found_article = False

    def process(self, elem):
        title = page_title(elem)
        print(title)
        if title == self.title:
            print(elem)
            self.found_article = True


def dump_pos(title, index):
    """returns byte position XML Dump from index file"""
    with bz2.BZ2File(index, 'r') as zh:
        for line in zh:
            spl = line.split()
            if " ".join(spl[:-1]) == title:
                return int(spl[-1])


def _main(title, index, dump):
    if index:
        pos = dump_pos(title, index)
        if not pos:
            raise StandardError("could not find dump pos in index!")
    pp = PullParser(title)
    with bz2.BZ2File(dump, 'r') as zh:
        if index:
            print("seek %d" % pos, file=sys.stderr)
            zh.seek(pos)
        while not pp.found_article:
            data = zh.read(CHUNK_SIZE)
            if not data:
                print("read %d bytes" % zh.tell())
                return
            pp.parse(data)


if __name__ == "__main__":
    desc = "Pull article from Wikipedia XML Dump"
    argp = argparse.ArgumentParser(description=desc)
    argp.add_argument("title", help="article title")
    argp.add_argument("dump", help="XML Dump bzip2 filename")
    argp.add_argument("-i", "-index", help="use index (bzip2) file")
    args = argp.parse_args()

    start = time.time()
    _main(args.title, args.i, args.dump)
    print("%5.3f seconds" % (time.time() - start), file=sys.stderr)
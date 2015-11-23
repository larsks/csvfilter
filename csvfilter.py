#!/usr/bin/env python

import argparse
import jinja2
import re
import sys
import unicodecsv as csv

from cStringIO import StringIO


class CSVFilter(object):
    def __init__(self, colspec, use_headers=True):
        self.colspec = colspec
        self.use_headers = use_headers
        self.env = jinja2.Environment()

    def reset(self):
        self.headers = {}
        self.header_list = []

    def filter(self, incsv, outcsv):
        self.reset()
        if self.use_headers:
            headers = incsv.next()
            self.header_list = headers
            self.headers = dict(zip(headers,
                                    range(len(self.header_list))))

        self.parse_colspec()

        if self.use_headers:
            outcsv.writerow(
                self.pick(self.header_list, apply_filters=False))

        for row in incsv:
            # just skip empty lines
            if not row:
                continue

            row = self.pick(row)
            outcsv.writerow(row)

    def pick(self, row, apply_filters=True):
        _row = []

        if self.use_headers:
            rowdict = dict(zip(self.header_list, row))
        else:
            rowdict = {}

        selected = set()

        for spec, filter in self._colspec:
            if isinstance(spec, slice):
                value = row[spec]
                selected.update(range(spec.start, spec.stop))
            elif isinstance(spec, int):
                value = [row[spec]]
                selected.add(spec)
            elif spec == '*':
                value = row
            elif spec == '%':
                value = [row[i] for i, val in enumerate(row)
                         if i not in selected]
            else:
                raise ValueError(spec)

            if apply_filters:
                _row.extend(filter(value=x, **rowdict) if filter else x
                            for x in value)
            else:
                _row.extend(value)

        return _row

    def parse_colspec(self):
        _colspec = []

        buf = StringIO(self.colspec)
        bufreader = csv.reader(buf)

        for spec in bufreader.next():
            if '|' in spec:
                spec, filter = spec.split('|', 1)
                filter = self.env.compile_expression('value|%s' % filter)
            else:
                filter = None

            if '-' in spec and not spec.startswith('-'):
                start, stop = spec.split('-')
                try:
                    start = int(start)
                except ValueError:
                    start = self.headers[start]

                try:
                    stop = int(stop)
                except ValueError:
                    stop = self.headers[stop]

                _colspec.append((slice(start, stop+1), filter))
            elif spec in ['*', '%']:
                _colspec.append((spec, filter))
            else:
                try:
                    _colspec.append((int(spec), filter))
                except ValueError:
                    _colspec.append((self.headers[spec], filter))

        self._colspec = _colspec


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument('--ifs', '-f',
                   default=',')
    p.add_argument('--ofs', '-F',
                   default=',')
    p.add_argument('--use-headers', '-H',
                   action='store_true')

    p.add_argument('colspec')
    p.add_argument('infile', nargs='?')
    p.add_argument('outfile', nargs='?')

    return p.parse_args()


def main():
    args = parse_args()

    with open(args.infile) if args.infile else sys.stdin as infd, \
            open(args.outfile, 'w') if args.outfile else sys.stdout as outfd:
    
        incsv = csv.reader(infd, delimiter=args.ifs)
        outcsv = csv.writer(outfd, delimiter=args.ofs, encoding='utf-8')
        filter = CSVFilter(args.colspec,
                           use_headers=args.use_headers)
        filter.filter(incsv, outcsv)

if __name__ == '__main__':
    main()


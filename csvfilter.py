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

        for rownum, row in enumerate(incsv):
            # just skip empty lines
            if not row:
                continue

            row = self.pick(rownum, row)
            outcsv.writerow(row)

    def pick(self, rownum, row):
        _row = []

        if self.use_headers:
            rowdict = dict(zip(self.header_list, row))
        else:
            rowdict = {}

        rowdict.update({
            '_csv_rownum': rownum,
            '_csv_columns': len(row),
        })

        for spec in self._colspec:
            if isinstance(spec, slice):
                _row.extend(row[spec])
            elif isinstance(spec, int):
                _row.append(row[spec])
            elif isinstance(spec, jinja2.environment.TemplateExpression):
                _row.append(spec(row=row,
                                 **rowdict))
            elif spec == '*':
                _row.extend(row)
            elif isinstance(spec, basestring) and spec.startswith('_csv'):
                _row.append(rowdict[spec])
            else:
                raise ValueError(spec)

        return _row

    def parse_colspec(self):
        _colspec = []

        buf = StringIO(self.colspec)
        bufreader = csv.reader(buf)

        for spec in bufreader.next():
            if '|' in spec or '[' in spec:
                _colspec.append(self.env.compile_expression(spec))
            elif '-' in spec and not spec.startswith('-'):
                start, stop = spec.split('-')
                if start.isdigit():
                    start = int(start)
                else:
                    start = self.headers[start]

                if stop.isdigit():
                    stop = int(stop)
                else:
                    stop = self.headers[stop]

                _colspec.append(slice(start, stop+1))
            elif spec.startswith('_csv'):
                _colspec.append(spec)
            elif spec == '*':
                _colspec.append(spec)
            else:
                try:
                    _colspec.append(int(spec))
                except ValueError:
                    _colspec.append(self.headers[spec])

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


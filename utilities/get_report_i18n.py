#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, time
from argparse import RawTextHelpFormatter, ArgumentParser
import argparse
import re

file_fr = "/home/robert/salome/git_repositories/fernuni/fsch_customer/i18n/fr_CH.po"
file_fr_out = (
    "/home/robert/git_repositories/fsch_customer/funid_reporting/i18n/fr_CH.po"
)

file_de = "/home/robert/salome/git_repositories/fernuni/fsch_customer/i18n/de.po"
file_de_out = "/home/robert/git_repositories/fsch_customer/funid_reporting/i18n/de.po"

file_en = "/home/robert/salome/git_repositories/fernuni/fsch_customer/i18n/en.po"
file_en_out = "/home/robert/git_repositories/fsch_customer/funid_reporting/i18n/en.po"


class Dumper(object):
    started = False  # is set when we found the first empty line
    hit_report = False  # is set when the word report is read
    out = None
    counter = 0
    line_counter = 0

    def __init__(self, fname, outname):
        self.fname = fname
        self.out = open(outname, "w")

    def dump_report(self, block):
        # print(''.join(block))
        self.counter += 1
        print(self.counter, len(block), self.line_counter)
        result = "".join(block)
        self.out.write(result)
        self.out.write("\n")
        block.clear()

    def dump(self):
        block = []
        hit_report = False
        with open(self.fname) as f:
            for line in f:
                self.line_counter += 1
                empty_line = not line.strip()
                if empty_line:
                    if hit_report:
                        self.dump_report(block)
                        hit_report = False
                    else:
                        block = []
                    continue
                if not hit_report:
                    hit_report = line.lower().find("report") > -1
                block.append(line)

        if block and hit_report:
            self.dump_report(block)

        self.out.close()


for fn, fno in [(file_fr, file_fr_out), (file_de, file_de_out), (file_en, file_en_out)]:
    dumper = Dumper(fn, fno)
    dumper.dump()

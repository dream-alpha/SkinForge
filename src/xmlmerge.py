#!/usr/bin/python
# encoding: utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import os
import sys
import getopt
import xml.etree.ElementTree as ET
from Version import VERSION


def merge_files(src1, src2, dst):
    tree1 = ET.parse(src1)
    root1 = tree1.getroot()

    tree2 = ET.parse(src2)
    root2 = tree2.getroot()

    root1.extend(root2)

    tree1.write(dst)


def xmlmerge(argv):
    print("xmlmerge %s" % VERSION)
    src1 = ""
    src2 = ""
    dst = ""
    opts = []

    try:
        opts, _args = getopt.getopt(argv, "i:j:o:", ["src1=", "src2=", "dst="])
    except getopt.GetoptError as e:
        print("Error: " + str(e))

    if len(opts) < 3:
        print('Usage: python xmlmerge.py -i <src1> -j <src2> -o <dst>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--src1"):
            src1 = os.path.normpath(arg)
        elif opt in ("-j", "--src2"):
            src2 = os.path.normpath(arg)
        elif opt in ("-o", "--dst"):
            dst = os.path.normpath(arg)

    print("merging skins...")
    print('src1: ' + src1)
    print('src2: ' + src2)
    print('dst: ' + dst)

    merge_files(src1, src2, dst)

    print("xmlmerge done.")


if __name__ == "__main__":
    xmlmerge(sys.argv[1:])

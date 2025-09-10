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


def get_width(filename):
    print("get_width: %s" % filename)
    svg_file = open(filename, 'r')
    tree = ET.parse(svg_file)
    root = tree.getroot()
    width = root.get('width')
    try:
        _fwidth = float(width)
    except Exception:
        width = 0
    print("get_width: %s" % width)
    return width


def scale_file(width, src, dst):
    os.popen("rsvg-convert -f svg -w %s %s -o %s" % (width, src, dst)).read()


def process_file(scale, src, dst):
    width = get_width(src)
    if width:
        width = int(float(scale) * float(width))
        scale_file(width, src, dst)
    else:
        print("process_file: no width in %s" % src)


def scale_svg(argv):
    print("svgscale %s" % VERSION)
    scale = ""
    src = ""
    dst = ""
    opts = []

    try:
        opts, _args = getopt.getopt(argv, "s:i:o:", ["scale=", "src=", "dst="])
    except getopt.GetoptError as e:
        print("Error: " + str(e))

    if len(opts) < 3:
        print('Usage: python svgscale.py -s <scale> -i <src> -o <dst>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-s", "--scale"):
            scale = arg
        elif opt in ("-i", "--src"):
            src = os.path.normpath(arg)
        elif opt in ("-o", "--dst"):
            dst = os.path.normpath(arg)

    if not dst:
        dst = src

    print("scaling svg...")
    print('scale: ' + scale)
    print('src: ' + src)
    print('dst: ' + dst)

    process_file(scale, src, dst)

    print("svgscale done.")


if __name__ == "__main__":
    scale_svg(sys.argv[1:])

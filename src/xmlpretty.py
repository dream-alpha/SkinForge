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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import os
import sys
import getopt
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from FileUtils import readFile, writeFile
from Version import VERSION


def listDir(adir):
    alist = []
    try:
        for afile in os.listdir(adir):
            # path = os.path.join(adir, afile)
            ext = os.path.splitext(afile)[1]
            if ext in [".xml", ".xmlinc"]:
                alist.append(afile)
    except OSError as e:
        print("failed: e: %s" % e)
    return alist


def add_root(lines):
    lines = ["<root>"] + lines + ["</root>"]
    return lines


def remove_root(ilines):
    olines = []
    for line in ilines:
        if line and not ("<root>" in line or "</root>" in line or "<?xml" in line):
            olines.append(line)
    # print("olines: %s" % olines)
    return olines


def process_file(src_file, dst_file):
    print("process_file: %s" % src_file)
    lines = readFile(src_file).splitlines()
    if os.path.splitext(src_file)[1] == ".xmlinc":
        lines = add_root(lines)
    xml_string = "\n".join(lines)
    tree = ET.ElementTree(ET.fromstring(xml_string))
    root = tree.getroot()
    try:
        # Handle Python 2/3 compatibility for ET.tostring parameters
        if sys.version_info[0] >= 3:
            # Python 3: tostring(element, encoding=None, method="xml")
            xml_string = ET.tostring(root, encoding="unicode", method="xml")
        else:
            # Python 2: tostring(element, encoding=None)
            xml_string = ET.tostring(root, encoding="utf-8")
            if isinstance(xml_string, bytes):
                xml_string = xml_string.decode("utf-8")

        # Parse and format with minidom
        xml_string = minidom.parseString(
            xml_string.encode("utf-8")).toprettyxml(indent="\t")

        # Handle encoding differences in toprettyxml output
        if isinstance(xml_string, bytes):
            xml_string = xml_string.decode("utf-8")

        # Fix attribute ordering differences between Python 2 and 3
        # Python 3 orders attributes alphabetically, Python 2 preserves source order
        # Reorder all attributes alphabetically for consistency
        xml_string = re.sub(
            r'<(\w+)\s+([^>]*?)/?>',
            lambda m: reorder_attributes_alphabetically(m.group(0)),
            xml_string
        )
    except Exception as e:
        print("exception in toprettyxml: %s\n%s" % (src_file, e))
    lines = [line for line in xml_string.splitlines() if line.split()]
    if os.path.splitext(src_file)[1] == ".xmlinc":
        lines = remove_root(lines)
    xml_string = "\n".join(lines)
    xml_string = xml_string.replace("&quot;", '"')
    xml_string += "\n"
    # print(xml_string)
    writeFile(dst_file, xml_string)


def process_files(src, dst):
    if os.path.isfile(src):
        process_file(src, dst)
    else:
        alist = listDir(src)
        for afile in alist:
            # print("afile: %s" % afile)
            if afile != "rcpositions.xml" and not afile.startswith("applet_"):
                process_file(os.path.join(src, afile),
                             os.path.join(dst, afile))


def xmlpretty(argv):
    print("xmlpretty %s" % VERSION)
    src = ""
    dst = ""
    opts = []

    try:
        opts, _args = getopt.getopt(argv, "i:o:", ["src=", "dst="])
    except getopt.GetoptError as e:
        print("Error: " + str(e))

    if len(opts) < 2:
        print('Usage: python xmlpretty.py -i <src file/dir> -o <dst file/dir>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--src"):
            src = os.path.normpath(arg)
        elif opt in ("-o", "--dst"):
            dst = os.path.normpath(arg)

    print("prettifying...")
    print('src file/dir: ' + src)
    print('dst file/dir: ' + dst)

    process_files(src, dst)

    print("xmlpretty done.")


def reorder_attributes_alphabetically(element_tag):
    """Reorder all element attributes alphabetically for consistent output between Python 2 and 3"""

    # Handle both self-closing tags and opening tags
    self_closing = element_tag.endswith('/>')

    # Extract tag name and attributes
    if self_closing:
        tag_match = re.match(r'<(\w+)\s+([^>]*?)/>', element_tag)
    else:
        tag_match = re.match(r'<(\w+)\s+([^>]*?)>', element_tag)

    if not tag_match:
        return element_tag

    tag_name = tag_match.group(1)
    attrs_string = tag_match.group(2) if tag_match.group(2) else ""

    # Extract all attributes
    attrs = {}
    attr_pattern = r'(\w+)="([^"]*)"'

    for match in re.finditer(attr_pattern, attrs_string):
        attr_name, attr_value = match.groups()
        attrs[attr_name] = attr_value

    # Build the reordered tag with alphabetically sorted attributes
    result = '<{}'.format(tag_name)

    for attr in sorted(attrs.keys()):
        result += ' {}="{}"'.format(attr, attrs[attr])

    # Preserve self-closing format
    if self_closing:
        result += '/>'
    else:
        result += '>'

    return result


if __name__ == "__main__":
    xmlpretty(sys.argv[1:])

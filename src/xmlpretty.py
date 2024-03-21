#!/usr/bin/python
# encoding: utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
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
		xml_string = ET.tostring(root, encoding="utf-8", method="xml")
		xml_string = minidom.parseString(xml_string).toprettyxml(indent="\t")
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
				process_file(os.path.join(src, afile), os.path.join(dst, afile))


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


if __name__ == "__main__":
	xmlpretty(sys.argv[1:])

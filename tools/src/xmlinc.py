#!/usr/bin/python
# encoding: utf-8
#
# Copyright (C) 2018-2023 by dream-alpha
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


def readFile(filename):
	with open(filename, "rb") as afile:
		data = afile.read()
	return data


def writeFile(path, data):
	with open(path, 'wb') as f:
		f.write(data)


def toInt(s):
	try:
		i = int(s)
	except Exception:
		i = s
	return i


def addMix(v1, v2):
	v1 = toInt(v1)
	v2 = toInt(v2)
	if isinstance(v1, str):
		r = v1
	elif isinstance(v2, str):
		r = v2
	else:
		r = v1 + v2
	return r


class Pos():
	def __init__(self, x, y=0):
		if isinstance(x, str):
			# print("Pos: __init__: x: %s" % x)
			if "," in x:
				pos_string = x.split(",")
				x = pos_string[0]
				if x.startswith("$"):
					x = self.globals[x]
				y = pos_string[1]
				if y.startswith("$"):
					y = self.globals[y]
		self.x = toInt(x)
		self.y = toInt(y)

	def __add__(self, other):
		new_x = addMix(self.x, other.x)
		new_y = addMix(self.y, other.y)
		return Pos(new_x, new_y)


class XMLInclude():
	def __init__(self, srcdir, dstdir, cmndir):
		self.srcdir = srcdir
		self.dstdir = dstdir
		self.cmndir = cmndir
		self.sep = (" ", '"', "{", "[", "(", ",", ":", "=", "}", "]", ")")
		self.globals = {}

	def clean(self, i):
		o = i.replace("\n", " ").replace("\t", " ")
		o = " ".join(o.split())
		o = o.replace("><", ">*<")
		o = o.replace("> <", ">*<")
		o = o.split("*")
		return o

	def split(self, s):
		r = []
		o = ""
		e = ""
		# print("split: s: %s" % s)
		if s.startswith("<"):
			s = s[1 :]
			r.append("<")
		if s.endswith("/>"):
			s = s[: -2]
			e = "/>"
		# print("split: s: %s" % s)
		for c in s:
			if c in self.sep:
				if o:
					r.append(o)
					o = ""
				r.append(c)
			else:
				o += c
		if o:
			r.append(o)
		if e:
			r.append(e)
		# print("split: r: %s" % r)
		return r

	def updatePos(self, words, pos):
		for i, word in enumerate(words):
			if 0 < i < len(words) - 1 and words[i - 1] != '"' and words[i + 1] == "=":
				if word in ["position"] and words[i + 2] == '"':  # or word in ["pos"] and words[i + 2] == "(":
					pos2 = Pos(words[i + 3], words[i + 5])
					# print("updatePos: pos2: (%s,%s)" % (pos2.x, pos2.y))
					new_pos = pos + pos2
					# print("updatePos: new_pos: (%s,%s)" % (new_pos.x, new_pos.y))
					words[i + 3] = str(new_pos.x)
					words[i + 5] = str(new_pos.y)
		return words

	def applyGlobals(self, words):
		for i, word in enumerate(words):
			if word == "=" and words[i + 1] == '"' and words[i + 2].startswith("$"):
				words[i + 2] = self.globals[words[i + 2]]
		return words

	def parseTags(self, words):
		tags = {}
		for i, word in enumerate(words):
			if word == "xmlinc":
				tags[word] = True
			elif word == "=":
				if words[i - 1] in ["position", "size"] and words[i + 1] == '"':
					tags[words[i - 1]] = "%s,%s" % (words[i + 2], words[i + 4])
				else:
					if words[i + 1] == '"':
						tags[words[i - 1]] = words[i + 2]
						if words[i - 1].startswith("$"):
							self.globals[words[i - 1]] = words[i + 2]
					else:
						tags[words[i - 1]] = words[i + 1]
		# print("parseTags: tags: %s" % tags)
		return tags

	def getIncFilePath(self, inc_filename):
		inc_file = os.path.join(self.srcdir, inc_filename) + ".xml"
		if not os.path.exists(inc_file):
			inc_file = os.path.join(self.srcdir, inc_filename) + ".xmlinc"
			if not os.path.exists(inc_file):
				inc_file = os.path.join(self.cmndir, inc_filename) + ".xml"
				if not os.path.exists(inc_file):
					inc_file = os.path.join(self.cmndir, inc_filename) + ".xmlinc"
		return inc_file

	def processFile(self, level, olines, afile, pos):
		print("=====> processFile: >%s, (%s,%s), %s)" % (level, pos.x, pos.y, afile))

		ilines = self.clean(readFile(afile))
		for iline in ilines:
			# print("processFile: iline: %s" % iline)
			iline_words = self.split(iline)
			iline_words = self.applyGlobals(iline_words)
			tags = self.parseTags(iline_words)
			# print("processFile: tags: %s" % tags)
			if "xmlinc" in tags:
				inc_filename = tags["name"]
				# print("processFile: inc_filename: %s" % inc_filename)
				pos2 = None
				if "position" in tags:
					pos2 = pos
					pos_string = tags["position"]
					# print("processFile: pos 1: %s" % pos_string)
					pos = pos + Pos(pos_string)
					# print("processFile: pos 2: (%s,%s)" % (pos.x, pos.y))
				inc_file = self.getIncFilePath(inc_filename)
				self.processFile(level + 1, olines, inc_file, pos)
				if pos2:
					pos = pos2
			else:
				# print("processFile: globals: %s" % self.globals)
				iline_words = self.updatePos(iline_words, pos)
				iline = "".join(iline_words)
				olines.append(iline)

		# print("<===== processFile: " + afile)
		return olines


def xmlinc(argv):
	print("xmlinc version 0.0.3")
	srcdir = ""
	dstdir = ""
	cmndir = ""
	opts = []
	try:
		opts, _args = getopt.getopt(argv, "i:o:c:", [])
	except getopt.GetoptError as e:
		print("Error: " + str(e))

	if len(opts) < 3:
		print('Usage: python xmlinc.py -i <srcfile> -o <dstdir> -c <cmndir>')
		sys.exit(2)

	for opt, arg in opts:
		if opt in ("-i"):
			srcfile = os.path.normpath(arg)
		elif opt in ("-o"):
			dstdir = os.path.normpath(arg)
		elif opt in ("-c"):
			cmndir = os.path.normpath(arg)

	print("processing xml...")
	print("src file: " + srcfile)
	srcdir = os.path.dirname(srcfile)
	print("src dir: " + srcdir)
	print("dst dir: " + dstdir)
	print("cmn dir: " + cmndir)

	olines = []
	olines = XMLInclude(srcdir, dstdir, cmndir).processFile(0, olines, srcfile, Pos(0, 0))
	output = "\n".join(olines) + "\n"
	writeFile(os.path.join(dstdir, os.path.basename(srcfile)), output)

	print("xmlinc done.")


if __name__ == "__main__":
	xmlinc(sys.argv[1:])

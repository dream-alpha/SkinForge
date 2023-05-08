#!/usr/bin/python
# encoding: utf-8
#
# Copyright (C) 2018-2023 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	For more information on the GNU General Public License see:
#	<http://www.gnu.org/licenses/>.


import os
import sys
import getopt
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


ending_values = ["Width", "Height", "Font", "Offset", "Margin", "HPos"]
key_values = ["xres", "yres", "lineSpacing", "value", "textX", "textY", "pixmapX", "pixmapY", "separation", "rcheight", "rcheighthalf", "font", "position", "size", "size2", "offset", "margin", "cornerDia", "selectionDia"]


def readFile(filename):
	with open(filename, "rb") as afile:
		data = afile.read()
	return data


def writeFile(path, data):
	with open(path, 'wb') as f:
		f.write(data)


def scale_value(scale, value):
	# print("scale_value: %s, %s" % (scale, value))
	try:
		if int(value) > 1:
			value = int(round(int(value) * float(scale)))
	except Exception:
		pass
	# print("scale_value: %s" % value)
	return str(value)


class Template():
	def __init__(self):
		self.sep = ("{", "[", "(", ",", ":", "=", "}", "]", ")")

	def clean(self, s):
		o = ""
		for c in s:
			if c not in [" ", "\n", "\t"]:
				o += c
		return o

	def split(self, s):
		r = []
		o = ""
		for c in s:
			if c in self.sep:
				if c in [",", ":"]:
					c += " "
				if o:
					r.append(o)
					o = ""
				r.append(c)
			else:
				o += c
		if o:
			r.append(o)
		return r

	def parse(self, scale, i):
		o = []
		n = 0
		while n < len(i):
			w = i[n]
			k = w.strip()
			if k in ["pos", "size"]:
				o.append("%s=(%s,%s)" % (k, scale_value(scale, i[n + 3]), scale_value(scale, i[n + 5])))
				n += 7
			elif k in ["gFont"]:
				o.append("%s(%s,%s)" % (k, scale_value(scale, i[n + 2]), scale_value(scale, i[n + 4])))
				n += 6
			elif k in ['"itemHeight"', '"itemWidth"']:
				o.append("%s:%s" % (k, scale_value(scale, i[n + 2])))
				n += 3
			elif k in [":"]:
				if i[n + 1] == "(":
					snum = i[n + 2]
					try:
						_inum = int(snum)
						o.append("%s(%s" % (k, scale_value(scale, i[n + 2])))
						n += 3
					except Exception:
						o.append(w)
						n += 1
				else:
					o.append(w)
					n += 1
			else:
				o.append(w)
				n += 1
		return o

	def scaleTemplate(self, scale, i):
		result = self.clean(i)
		# print("clean:\n%s" % result)
		result = self.split(result)
		# print("split:\n%s" % result)
		result = self.parse(scale, result)
		# print("parse:\n%s" % result)
		result = "".join(result)
		# print("join:\n%s" % result)
		return result


class XML(Template):
	def __init__(self):
		Template.__init__(self)
		self.pixmaps_to_be_scaled = []

	def scale_column(self, scale, key, value):
		# print("key: %s, value: %s" % (key, value))
		out = value
		if "," in value:
			numbers = value.split(",")
			out = "%s,%s,%s,%s,%s,%s,%s" % (scale_value(scale, numbers[0]), scale_value(scale, numbers[1]), numbers[2], numbers[3], scale_value(scale, numbers[4]), numbers[5], numbers[6])
		# print("scale_column: %s" % out)
		return out

	def scale_number(self, scale, key, value):
		# print("key: %s, value: %s" % (key, value))
		out = str(value)
		if key in key_values or any(key.endswith(end) for end in ending_values):
			if "," in value:
				numbers = value.split(",")
				try:
					int0 = int(numbers[0])
				except Exception:
					int0 = None
				try:
					int1 = int(numbers[1])
				except Exception:
					int1 = None
				if int0 or int1:
					out = "%s,%s" % (scale_value(scale, numbers[0]), scale_value(scale, numbers[1]))
			elif ";" in value:
				numbers = value.split(";")
				out = "%s;%s" % (numbers[0], scale_value(scale, numbers[1]))
			else:
				out = scale_value(scale, value)
		# print("out: %s" % out)
		return str(out)

	def add_root(self, src):
		has_root = False
		lines = readFile(src).splitlines()
		for line in lines:
			if "<skin>" in line:
				has_root = True
				break
		else:
			lines = ["<root>"] + lines + ["</root>"]
		result = "\n".join(lines)
		return has_root, result

	def remove_root(self, lines):
		for i, line in enumerate(lines):
			if "<root>" in line:
				del lines[i]
		if "</root>" in lines[len(lines) - 1]:
			del lines[len(lines) - 1]
		return lines

	def process_file(self, scale, src, dst):
		has_root, xml_string = self.add_root(src)
		tree = ET.ElementTree(ET.fromstring(xml_string))
		root = tree.getroot()
		for node in tree.iter():
			for elem in node:  # .iter():
				# print(node.tag, elem.tag)
				if not (node.tag == "skin" and elem.tag == "screen" and "id" in elem.attrib):
					if node.tag == "widget" and elem.tag == "convert" and elem.attrib["type"] == "TemplatedMultiContent":
						if elem.text:
							elem.text = self.scaleTemplate(scale, elem.text)
					else:
						for key in elem.attrib:
							# print("--- ", key, elem.attrib[key])
							if key.startswith("column"):
								elem.attrib[key] = self.scale_column(scale, key, elem.attrib[key])
							else:
								elem.attrib[key] = self.scale_number(scale, key, elem.attrib[key])
							if key in ["backgroundPixmap", "selectionPixmap"]:
								key_value = elem.attrib[key]
								if os.path.splitext(key_value)[1] == ".svg" and key_value not in self.pixmaps_to_be_scaled:
									self.pixmaps_to_be_scaled.append(elem.attrib[key])

		xml_string = ET.tostring(root, encoding="utf-8", method="xml")
		xml_string = minidom.parseString(xml_string).toprettyxml(indent="\t")
		lines = [line for line in xml_string.splitlines() if line.split()]
		# print(lines)
		if not has_root:
			lines = self.remove_root(lines)
		# print(lines)
		if os.path.splitext(src)[1] == ".xmlinc":
			print("deleting first line")
			del lines[0]
		# print(lines)
		xml_string = "\n".join(lines)
		xml_string = xml_string.replace("&quot;", '"') + "\n"
		# print(xml_string)
		writeFile(dst, xml_string)
		if self.pixmaps_to_be_scaled:
			writeFile(os.path.join(os.path.dirname(dst), "pixmaps_to_be_scaled.txt"), "\n".join(self.pixmaps_to_be_scaled))

def scale_skin(argv):
	print("xmlscale version 0.0.2")
	scale = ""
	src = ""
	dst = ""
	opts = []

	try:
		opts, _args = getopt.getopt(argv, "s:i:o:", ["scale=", "src=", "dst="])
	except getopt.GetoptError as e:
		print("Error: " + str(e))

	if len(opts) < 3:
		print('Usage: python xmlscale.py -s <scale> -i <src> -o <dst>')
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

	print("processing skin...")
	print('scale: ' + scale)
	print('src: ' + src)
	print('dst: ' + dst)

	XML().process_file(scale, src, dst)

	print("xmlscale done.")


if __name__ == "__main__":
	scale_skin(sys.argv[1:])

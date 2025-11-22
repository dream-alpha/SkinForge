#!/usr/bin/python
# coding=utf-8
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
import re
import sys
import getopt
from xmlscale import XML as Scale
from FileUtils import readFile, writeFile
from Pos import Pos
from Version import VERSION


def getScale(adir):
    name = os.path.basename(adir)
    scale = 1.0
    if name in ["Default-HD"]:
        scale = 2.0 / 3.0
    elif name in ["Default-WQHD", "Other-WQHD"]:
        scale = 4.0 / 3.0
    # print("getScale: scale: %s" % scale)
    return scale


class XMLInclude():
    def __init__(self, srcdir, dstdir, cmndir):
        self.srcdir = srcdir
        self.dstdir = dstdir
        self.cmndir = cmndir
        self.sep1 = (
            " ", '"', "{", "[", "(", ",", ";", ":", "=", "}", "]", ")")
        self.sep2 = ("+", "-", "*", "/", "%")
        self.globals = {}
        self.layouts = []
        self.colors = {}
        colors_file, delete = self.getIncFilePath("colors")
        self.parseColors(colors_file)
        if delete:
            os.system("rm %s" % colors_file)
        colors_file, delete = self.getIncFilePath("skin_src.xml")
        self.parseColors(colors_file)
        if delete:
            os.system("rm %s" % colors_file)

    def clean(self, i):
        o = i.replace("\n", " ").replace("\t", " ")
        o = " ".join(o.split())
        o = o.replace("><", ">Â§<")
        o = o.replace("> <", ">Â§<")
        o = o.split("Â§")
        return o

    def split(self, s, sep):
        o = []
        b = ""
        e = ""

        # print("split: s: %s" % s)
        if s.startswith("</"):
            s = s[2:]
            b = "</"
        elif s.startswith("<"):
            s = s[1:]
            b = "<"
        if s.endswith("/>"):
            s = s[:-2]
            e = "/>"
        elif s.endswith(">"):
            s = s[:-1]
            e = ">"

        pattern = '({})'.format('|'.join(re.escape(c) for c in sep))
        r = re.split(pattern, s)
        r = [item for item in r if item != '']

        if b:
            o.append(b)
        o += r
        if e:
            o.append(e)
        # print("split: o: %s" % o)
        return o

    def updatePositions(self, words, pos):
        for i, word in enumerate(words):
            if 0 < i < len(words) - 1 and words[i - 1] != '"' and words[i + 1] == "=":
                if word == "position" and words[i + 2] == '"':
                    pos2 = Pos(words[i + 3], words[i + 5])
                    # print("updatePositions: pos2: (%s,%s)" % (pos2.x, pos2.y))
                    new_pos = pos + pos2
                    # print("updatePositions: new_pos: (%s,%s)" % (new_pos.x, new_pos.y))
                    words[i + 3] = str(new_pos.x)
                    words[i + 5] = str(new_pos.y)
        return words

    def parseColors(self, colors_inc):
        print("parseColors: colors_inc: %s" % colors_inc)
        if os.path.exists(colors_inc):
            ilines = self.clean(readFile(colors_inc))
            for iline in ilines:
                # print("parseColors: iline: %s" % iline)
                iline_words = self.split(iline, self.sep1)
                if iline_words[1] == "color":
                    tags = self.parseTags(iline_words)
                    # print("parseColors: tags: %s" % tags)
                    if "name" in tags and "value" in tags:
                        self.colors["$" + tags["name"]] = tags["value"]
        # print("parseColors: self.colors: %s" % self.colors)

    def evaluateFormulas(self, words):
        # print("eval: words: %s" % words)
        output = []
        i = 0
        while i < len(words):
            if words[i] == "eval":
                formula = ""
                i += 1
                level = 0
                while level > 0 or not formula:
                    if words[i] in ("(", ")"):
                        level += 1 if words[i] == "(" else -1
                    formula += words[i]
                    i += 1

                # Debug: Print what we're evaluating
                # print("DEBUG: evaluating formula: %s" % formula)

                # Handle Python 2/3 division compatibility
                # For pixel calculations, we almost always want integer division
                # Replace single '/' with '//' to ensure consistent behavior
                original_formula = formula
                formula = re.sub(r'(?<!/)/(?!/)', '//', formula)
                if formula != original_formula:
                    # print("DEBUG: formula changed from %s to %s" % (original_formula, formula))
                    pass

                # Evaluate the formula and ensure consistent integer results
                eval_result = eval(formula)
                # print("DEBUG: eval result: %s, type: %s" % (eval_result, type(eval_result)))

                # For positioning calculations, we want integer results
                # Use consistent rounding behavior between Python 2 and 3
                if isinstance(eval_result, float):
                    # Use Python 2 style rounding: round half away from zero
                    import math
                    if eval_result >= 0:
                        result = int(math.floor(eval_result + 0.5))
                    else:
                        result = int(math.ceil(eval_result - 0.5))
                else:
                    result = int(eval_result)

                # print("DEBUG: final result: %s" % result)
                output.append(str(result))
            else:
                output.append(words[i])
                i += 1
        # print("output: %s" % output)
        return output

    def checkValue(self, value):
        # print("checkValue: value: %s" % value)
        if value != "center":
            _i = int(value)

    def checkFonts(self, tags):
        # print("checkFonts: %s" % tags)
        for tag in tags:
            if tag == "font" and "size" in tags:
                font_parts = tags["font"].split(";")
                if len(font_parts) > 1:
                    font_size = font_parts[1]
                    size_height = tags["size"].split(",")[1]
                    if float(size_height) < float(font_size) * 4.0 / 3.0:
                        print("WARNING: size: %s < font: %s" %
                              (size_height, float(font_size) * 4.0 / 3.0))

    def parseTags(self, words):
        tags = {}
        for i, word in enumerate(words):
            if word == "xmlinc":
                tags[word] = words[words.index("file") + 3]
            elif word in ["screen", "layout", "global"]:
                tags[word] = words[-1]
            elif word == "=":
                if words[i + 1] == '"':
                    # print("words 1: %s" % words)
                    if words[i - 1] in ["size"]:
                        self.checkValue(words[i + 2])
                        if words[i + 3] == ",":
                            self.checkValue(words[i + 4])
                            tags[words[i - 1]] = f"{words[i + 2]},{words[i + 4]}"
                        else:
                            tags[words[i - 1]] = f"{words[i + 2]}"
                    elif words[i - 1] in ["font"]:
                        # print("words: %s", words)
                        if words[i + 3] == ";":
                            self.checkValue(words[i + 4])
                            tags[words[i - 1]] = f"{words[i + 2]};{words[i + 4]}"
                    elif words[i - 1] in ["position"]:
                        self.checkValue(words[i + 2])
                        self.checkValue(words[i + 4])
                        tags[words[i - 1]] = "%s,%s" % (words[i + 2], words[i + 4])
                    elif words[i - 1].endswith("Color"):
                        # print(">>> %s = %s" % (words[i - 1], words[i + 2]))
                        if not words[i + 2].startswith("#") and words[i + 2] != "(":
                            color = words[i + 2]
                            if "$" + color not in self.colors and color not in self.colors:
                                raise Exception("color %s not defined" % color)
                        tags[words[i - 1]] = words[i + 2]
                    else:
                        tags[words[i - 1]] = words[i + 2]
                else:
                    tags[words[i - 1]] = words[i + 1]
        # print("parseTags: words: %s" % words)
        # print("parseTags: tags: %s" % tags)
        return tags

    def parseGlobals(self, tags):
        if "global" in tags:
            self.globals["$" + tags["name"]] = tags["value"]
        elif "screen" in tags:
            # print("parseGlobals: tags: %s" % tags)
            if "size" in tags:
                size = tags["size"].split(",")
                self.globals["$screen_width"] = size[0]
                self.globals["$screen_height"] = size[1]
        elif tags and "layout" in tags and tags["layout"] == ">":
            # print(">>> adding layout: %s" % tags["name"])
            self.layouts.append(tags["name"])
        elif "xmlinc" in tags:
            for tag in tags:
                # print("parseGlobals: %s - %s -> %s" % (tags["xmlinc"], tag, tags[tag]))
                if tag == "size":
                    size = tags[tag].split(",")
                    self.globals["$width"] = size[0]
                    self.globals["$height"] = size[1]
                else:
                    self.globals["$" + tag] = tags[tag]
        # print("parseTags: tags: %s" % tags)
        # print("parseTags: globals: %s" % self.globals)

    def getIncFilePath(self, inc_filename):
        noop = ":"
        if not os.path.splitext(inc_filename)[1]:
            inc_filename += ".xmlinc"
        # print("inc_filename: %s" % inc_filename)

        inc_file = os.path.join(self.dstdir, inc_filename)
        copy1 = noop
        copy2 = noop
        do_scale = False
        do_delete = False
        # print("inc_file: %s" % inc_file)

        if not os.path.exists(inc_file):
            inc_file = os.path.join(self.cmndir, inc_filename)
            copy1 = "cp %s %s" % (
                inc_file, os.path.join(self.dstdir, inc_filename))
            copy2 = noop
            do_scale = False
            do_delete = False
            # print("inc_file: %s" % inc_file)

            if not os.path.exists(inc_file):
                inc_file = os.path.join(
                    os.path.dirname(self.dstdir), inc_filename)
                copy1 = noop
                copy2 = "cp %s %s" % (
                    inc_file, os.path.join(self.dstdir, inc_filename))
                # print("inc_file: %s" % inc_file)
                if not os.path.exists(inc_file):
                    inc_file = os.path.join(
                        os.path.dirname(self.cmndir), inc_filename)
                    copy1 = "cp %s %s" % (inc_file, os.path.join(
                        os.path.dirname(self.dstdir), inc_filename))
                    copy2 = "cp %s %s" % (os.path.join(os.path.dirname(
                        self.dstdir), inc_filename), os.path.join(self.dstdir, inc_filename))
                    # print("inc_file: %s" % inc_file)
                    if not os.path.exists(inc_file):
                        Exception("inc file: %s not found." % inc_file)
                do_scale = True
                do_delete = True

        # print("inc_file found: %s" % inc_file)
        # print("do_scale: %s" % do_scale)
        # print("do_delete: %s" % do_delete)
        # print("copying 1: %s" % copy1)
        os.system(copy1)
        # print("copying 2: %s" % copy2)
        os.system(copy2)

        inc_file = os.path.join(self.dstdir, inc_filename)
        scale = getScale(self.dstdir)
        if scale != 1.0 and "Summary" not in inc_file and do_scale:
            print("--> Scale: %s" % inc_file)
            Scale().processFile(scale, inc_file, inc_file)
        return inc_file, do_delete

    def resolveGlobals(self, words):
        owords = []
        for word in words:
            if word.startswith("$"):
                if word in self.colors:
                    owords.append(self.colors[word])
                elif word in self.globals:
                    owords.append(self.globals[word])
                else:
                    try:
                        i = int(word.strip("$"))
                        owords.append(str(i))
                    except Exception:
                        Exception("global %s not found." % word)
            else:
                owords.append(word)
        oline = "".join(owords)
        # print("+++ oline: %s" % oline)
        return oline

    def processApplet(self, level, olines, afile):
        print("==> processApplet:  >%s, %s)" % (level, afile))
        ilines = readFile(afile).splitlines()
        for iline in ilines:
            olines.append(iline)

    def processFile(self, level, olines, afile, pos, do_delete):
        print("==> processFile: >%s, (%s,%s), %s, do_delete: %s" %
              (level, pos.x, pos.y, afile, do_delete))
        if level == 0 and not os.path.isfile(afile):
            afile, do_delete = self.getIncFilePath(afile)
        if level == 1:
            print("")

        ilines = self.clean(readFile(afile))
        for iline in ilines:
            # print("processFile: iline: %s" % iline)
            iline_words = self.split(iline, self.sep1 + self.sep2)
            if "$" in iline:
                iline = self.resolveGlobals(iline_words)
            iline_words = self.split(iline, self.sep1)
            if "eval" in iline_words:
                iline_words = self.evaluateFormulas(iline_words)
            tags = self.parseTags(iline_words)
            if "Summary" not in afile:
                self.checkFonts(tags)
            self.parseGlobals(tags)
            if "layout" in tags:
                # print("tags: %s" % tags)
                if "layout" in tags and tags["layout"] == "/>":
                    # print(">>>> tags: %s, layouts: %s" % (tags["name"], self.layouts))
                    if level == 1:
                        print("")
                    if not tags["name"] in self.layouts:
                        print("==> processFile: >%s, ERROR: layout %s not defined" % (
                            level, tags["name"]))
                    print("==> processFile: >%s, >>> including layout %s" %
                          (level, tags["name"]))
            if "xmlinc" in tags:
                inc_filename = tags["xmlinc"]
                # print("processFile: inc_filename: %s" % inc_filename)
                pos2 = pos
                if "position" in tags:
                    # print("processFile: tags.position: %s" % tags["position"])
                    pos2 = pos + Pos(tags["position"])
                    # print("processFile: pos2: (%s,%s)" % (pos2.x, pos2.y))
                inc_file, next_delete = self.getIncFilePath(inc_filename)
                if os.path.basename(inc_file).startswith("applet_"):
                    self.processApplet(level + 1, olines, inc_file)
                else:
                    self.processFile(level + 1, olines,
                                     inc_file, pos2, next_delete)
                # print("-----> processFile: continue with: " + afile)
            elif "global" in tags:
                pass
            else:
                # print("processFile: globals: %s" % self.globals)
                if "position" in iline_words:
                    iline_words = self.updatePositions(iline_words, pos)
                iline = "".join(iline_words)
                olines.append(iline)

        if do_delete:
            # print("rm %s" % afile)
            os.system("rm %s" % afile)

        # print("<===== processFile: >%s" + (level, afile))


def xmlinc(argv):
    print("xmlinc %s" % VERSION)
    srcinfile = ""
    srcoutfile = ""
    dstdir = ""
    cmndir = ""
    opts = []
    try:
        opts, _args = getopt.getopt(argv, "i:o:d:c:", [])
    except getopt.GetoptError as e:
        print("Error: " + str(e))

    if len(opts) < 4:
        print(
            'Usage: python xmlinc.py -i <srcinfile> -o <srcoutfile> -d <dstdir> -c <cmndir>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-i":
            srcinfile = os.path.normpath(arg)
        elif opt == "-o":
            srcoutfile = os.path.normpath(arg)
        elif opt == "-d":
            dstdir = os.path.normpath(arg)
        elif opt == "-c":
            cmndir = os.path.normpath(arg)

    print("processing xml...")
    print("src in file: " + srcinfile)
    srcdir = os.path.dirname(srcinfile)
    print("src out file: " + srcoutfile)
    print("src dir: " + srcdir)
    print("dst dir: " + dstdir)
    print("cmn dir: " + cmndir)

    olines = []
    XMLInclude(srcdir, dstdir, cmndir).processFile(
        0, olines, "skin_src.xml", Pos(0, 0), False)
    output = "\n".join(olines) + "\n"
    writeFile(srcoutfile, output)

    print("xmlinc done.")


if __name__ == "__main__":
    xmlinc(sys.argv[1:])

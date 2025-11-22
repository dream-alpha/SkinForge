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
                y = pos_string[1]
        self.x = toInt(x)
        self.y = toInt(y)

    def __add__(self, other):
        new_x = addMix(self.x, other.x)
        new_y = addMix(self.y, other.y)
        return Pos(new_x, new_y)

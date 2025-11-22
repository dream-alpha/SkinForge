# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


import os
import sys
import glob
from Debug import logger

# Python 2/3 compatibility for quote function
try:
    from pipes import quote
except ImportError:
    from shlex import quote


def stripCutNumber(path):
    filename, ext = os.path.splitext(path)
    if len(filename) > 3:
        if filename[-4] == "_" and filename[-3:].isdigit():
            filename = filename[:-4]
        path = filename + ext
    return path


def readFile(path):
    data = ""
    try:
        # Open with explicit encoding for Python 3 compatibility
        if sys.version_info[0] >= 3:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
        else:
            with open(path, "r") as f:  # pylint: disable=unspecified-encoding
                data = f.read()
    except Exception as e:
        logger.info("path: %s, exception: %s", path, e)
    return data


def writeFile(path, data):
    try:
        # Open with explicit encoding for Python 3 compatibility
        if sys.version_info[0] >= 3:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
        else:
            with open(path, "w") as f:  # pylint: disable=unspecified-encoding
                f.write(data)
    except Exception as e:
        logger.error("path: %s, exception: %s", path, e)


def deleteFile(path):
    os.popen("rm %s" % quote(path)).read()


def deleteFiles(path, clear=False):
    for afile in glob.glob(path):
        if clear:
            writeFile(afile, "")
        os.remove(afile)


def touchFile(path):
    os.popen("touch %s" % quote(path)).read()


def copyFile(src_path, dest_path):
    os.popen("cp %s %s" % (quote(src_path), quote(dest_path))).read()


def renameFile(src_path, dest_path):
    os.popen("mv %s %s" % (quote(src_path), quote(dest_path))).read()


def createDirectory(path):
    os.popen("mkdir -p %s" % quote(path)).read()


def createSymlink(src, dst):
    logger.info("link: src: %s > %s", src, dst)
    os.symlink(src, dst)


def deleteDirectory(path):
    os.popen("rm -rf %s" % quote(path)).read()

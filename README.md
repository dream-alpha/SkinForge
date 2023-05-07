# SkinForge - A toolset for creating and "hammering" enigma2 skins

## Introduction
An enigma2 skin is a flat xml data structure, no hierarchical includes, no macros, no relative positioning of screen elements, no high level framework, no automatic scaling... no nothing. :-)

## Motivation
So, creating and scaling skins for enigma2 is a task for someone who has killed their father and mother.
If you have a set of plugins you probably would like to have the same look and feel across all plugins. You may also want to maintain changes of skin elements only in one spot instead of having to maintain multiple instances of the same code in several plugins.

## Objective
I came up with an object oriented approach that sort of provides data encapsulation, inheritance, and reuse of skin elements across multiple skin screens and plugins.
In addition the solution allows for relative positions of skin elements, and automatic scaling of skin elements or complete skins.


## Status
This project is work in progress.

Tools available:
- xmlscale:
```
    xmlscale <scale> <input-file> <outpout-file>
```
- svgscale (only works on pc, as librsvg2-bin is not available on the box):
```
    svgscale <scale> <svg-file>
```
- svgscaledir (including subdirs):
```
    svgscaldir <scale> <dir>
```


## Installation
No package available, just clone the git: "git clone git@github.com:dream-alpha/SkinForge.git"


## Example for relative skin includes
main file: Example.xml

    <skin>
        <screen>
            <xmlinc name=buttons position="100,200" />
        </screen>
    </skin>

include file: buttons.xmlinc

    <ePixmap pixmap="Default-FHD/skin_default/buttons/red.svg" position="0,0" size="300,70" />
    <ePixmap pixmap="Default-FHD/skin_default/buttons/green.svg" position="300,0" size="300,70" />
    <ePixmap pixmap="Default-FHD/skin_default/buttons/yellow.svg" position="600,0" size="300,70" />
    <ePixmap pixmap="Default-FHD/skin_default/buttons/blue.svg" position="900,0" size="300,70" />

The position of the red button will be: "100,200", the position of the green button will be "400,200".

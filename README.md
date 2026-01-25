# Cave and Cave-Plus archives

# What is this?

Cave (and later Cave-Plus) were MUDs for the [BBC Micro](https://en.wikipedia.org/wiki/BBC_Micro), initially released back in 1985.

This repository contains original dumps of the source code (from a few different places).  I make no claims whatsoever regarding the copyright.

# Source in Text

The original BBC BASIC files have been detokenised, thanks to ```BBCBasicToText.py``` which is in the scripts directory.  Please note that this needs Python2 to work correctly.

For Cave-Plus, a lot of the code has been fully annotated which explains how the game actually works.

# The remakes

Some years back, I ported a version of Cave to run via telnet under the Ranvier MUD system: https://github.com/tgreaves/ranviermud-cave

More recently, I have created an 'authentic' edition that can be played via a web browser.  This edition more accurately simulates running on an actual BBC Micro (including the use of MODE 7 graphics and floppy disk sound effects). https://github.com/tgreaves/ranviermud-cave

You can play the latter version directly by visiting: http://cave.extricae.org:1985

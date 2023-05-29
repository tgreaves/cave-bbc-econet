# Cave and Cave-Plus archives

# What is this?

Cave (and later Cave-Plus) were MUDs for the [BBC Micro](https://en.wikipedia.org/wiki/BBC_Micro), initially released back in 1985.

This repository contains original dumps of the source code (from a few different places).  I make no claims whatsoever regarding the copyright.

# Source in Text

The original BBC BASIC files have been detokenised, thanks to ```BBCBasicToText.py``` which is in the scripts directory.  Please note that this needs Python2 to work correctly.

# The remake

You don't need the original hardware (including Econet!) to enjoy Cave.  I put together a remodelling using the Ranvier MUD system: https://github.com/tgreaves/ranviermud-cave

# Code notes

## Cave initialisation / locations

When the first player enters the Cave, OBJINIT is loaded which sets object locations.

In Cave-Plus, items are placed in random locations, but not areas 16-20 (Wizard's Room and surrounding areas).

```DEFPROCU:FORN=(k+1)TOZ:REPEATT=RND(b):UNTILT>20ORT<16:!(&A00+(N*4))=T:NEXT:ENDPROC```

Note that in both versions, mobs are placed in pre-determined initial locations as defined in the DATA file.

# -*- coding: utf-8 -*-
"""
Connection screen

This is the text to show the user when they first connect to the game (before
they log in).

To change the login screen in this module, do one of the following:

- Define a function `connection_screen()`, taking no arguments. This will be
  called first and must return the full string to act as the connection screen.
  This can be used to produce more dynamic screens.
- Alternatively, define a string variable in the outermost scope of this module
  with the connection string that should be displayed. If more than one such
  variable is given, Evennia will pick one of them at random.

The commands available to the user when the connection screen is shown
are defined in evennia.default_cmds.UnloggedinCmdSet. The parsing and display
of the screen is done by the unlogged-in "look" command.

"""

from django.conf import settings

CONNECTION_SCREEN = """
|b==========================================================================|n

  |c 
       ____                      __    ___  _     _           _           
    / ___│  ___  __ _    ___  / _│  / _ ╲│ │__ (_) ___  ___│ │_ ___     
    ╲___ ╲ / _ ╲/ _` │  / _ ╲│ │_  │ │ │ │ '_ ╲│ │/ _ ╲/ __│ __/ __│    
     ___) │  __/ (_│ │ │ (_) │  _│ │ │_│ │ │_) │ │  __/ (__│ │_╲__ ╲    
    │____/ ╲___│╲__,_│  ╲___/│_│    ╲___/│_.__// │╲___│╲___│╲__│___/    
                                             │__/         |n  %s

  A community that must decide together what is worth keeping -- or sink.

|b--------------------------------------------------------------------------|n

  If you have an existing account, connect to it by typing:
       |wconnect <username> <password>|n
  If you need to create an account, type (without the <>'s):
       |wcreate <username> <password>|n

  If you have spaces in your username, enclose it in quotes.
  Enter |whelp|n for more info. |wlook|n will re-show this screen.

|b==========================================================================|n""" % settings.GAME_SLOGAN

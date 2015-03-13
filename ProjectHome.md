this python project takes an animated .gif (or multiple single images) as the input and outputs an animated .vtf spray using the vtex compiler in the source SDK.

uses imagemagick to split the .gif files into .tga files. resizes the images appropriately, calls the vtex compiler.

built with gtk+ 2.1.6, [pygtk](http://www.pygtk.org/), [py2exe](http://www.py2exe.org/), python 2.6.5 on windows

**Development is completed unless someone comes up with new feature requests or reports bugs**

May require Visual c++ runtimes available from microsoft [here](http://www.microsoft.com/downloads/details.aspx?familyid=A5C84275-3B97-4AB7-A40D-3802B2AF5FC2&displaylang=en)

[1.3.4](http://code.google.com/p/spraygen/downloads/list)
  * Changed maximum VTF spray size to 512kb to match new file size limit on source games

[1.3.3](http://code.google.com/p/spraygen/downloads/list)
  * replaced crappy GTK file dialogs with native window dialogs. MUCH nicer.

[1.3.2](http://code.google.com/p/spraygen/downloads/list)
  * support importing single images to create animation (.jpg, .png, .tga)

[1.3.1](http://code.google.com/p/spraygen/downloads/list)
  * support adding single frame files for fading spray (.jpg, .png, .tga)
  * misc bugfixes

[1.3](http://code.google.com/p/spraygen/downloads/list)
  * support for [fading sprays](http://www.youtube.com/watch?v=So_AjBQYEMY) from gif frames (jpg support soon)
  * if the calculated frames in the VTF are 0, highlight in red.

[1.2.4](http://code.google.com/p/spraygen/downloads/list)
  * fixed steam error "game is unavailable"
  * no longer requires steam to be running
  * auto-install for L4D/L4D2 edits your autoexec.cfg to select the spray for you

[1.2.3](http://code.google.com/p/spraygen/downloads/list)
  * Fixed steam detection error
  * Fixed a ton of misc errors
  * Added ability to save file as well as auto-install
  * Auto install for TF2, CS:S works, L4D and L4D2 you will have to import manually
  * Added Tooltips
  * Code Cleanup
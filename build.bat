python setup.py py2exe
del /q tga\*.tga
del /q vtex\materialsrc\vgui\logos\*.*
del /q vtex\materials\vgui\logos\*.*
xcopy /e /y tga dist\tga\
xcopy /e /y vtex dist\vtex\
xcopy /e /y gtk\etc dist\etc\
xcopy /e /y gtk\lib dist\lib\
xcopy /e /y gtk\share dist\share\
xcopy /e /y imagemagick dist\imagemagick\

python setup.py py2exe
del /q tga\*.tga
del /q tga\*.gif
del /q vtfcmd\*.tga
del /q vtfcmd\*.dds
del /q vtfcmd\*.vtf
del /q vtex\materialsrc\vgui\logos\*.*
del /q vtex\materials\vgui\logos\*.*
xcopy /e /y tga dist\tga\
xcopy /e /y vtex dist\vtex\
xcopy /e /y gtk\etc dist\etc\
xcopy /e /y gtk\lib dist\lib\
xcopy /e /y gtk\share dist\share\
xcopy /e /y imagemagick dist\imagemagick\
xcopy /e /y vtfcmd dist\vtfcmd\
copy msvcr90.dll dist
del dist\w9xpopen.exe
#!/usr/bin/env python
import pygtk
import gtk
import os
#import sys
import string
from _winreg import ConnectRegistry, OpenKey, HKEY_CURRENT_USER, QueryValueEx
from math import log, floor

workingdir = os.getcwd()
magicnumber = 180224 # max size for TGAs in VTF

# natural sort functions
def try_int(s):
    "Convert to integer if possible."
    try: return int(s)
    except: return s

def natsort_key(s):
    "Used internally to get a tuple by which s is sorted."
    import re
    return map(try_int, re.findall(r'(\d+|\D+)', s))

def natcmp(a, b):
    "Natural string comparison, case sensitive."
    return cmp(natsort_key(a), natsort_key(b))

def natcasecmp(a, b):
    "Natural string comparison, ignores case."
    return natcmp(a.lower(), b.lower())

def natsort(seq, cmp=natcmp):
    "In-place natural string sort."
    seq.sort(cmp)
    
def natsorted(seq, cmp=natcmp):
    "Returns a copy of seq, sorted by natural string sort."
    import copy
    temp = copy.copy(seq)
    natsort(temp, cmp)
    return temp


class mainwindow:
    builder = gtk.Builder()
    builder.add_from_file("spraygen.xml")
    def __init__(self):
        self.window = self.builder.get_object("window1")
        # stop program when window closes
        dic = { "on_button1_clicked" : self.convert, "on_window1_destroy" : gtk.main_quit, "on_radiobutton1_toggled" : self.sizechanged, "on_radiobutton2_toggled" : self.sizechanged, "on_radiobutton3_toggled" : self.sizechanged, "on_radiobutton4_toggled" : self.sizechanged, "on_radiobutton5_toggled" : self.sizechanged, "on_radiobutton6_toggled" : self.sizechanged, "on_radiobutton7_toggled" : self.sizechanged, "on_radiobutton8_toggled" : self.sizechanged, "on_radiobutton9_toggled" : self.sizechanged, "on_radiobutton10_toggled" : self.sizechanged, "on_transparencybutton_toggled" : self.sizechanged, "on_filechooserbutton1_file_set" : self.fileselected }
        self.builder.connect_signals(dic)
        filefilter = gtk.FileFilter()
        filefilter.add_pattern("*.gif")
        self.builder.get_object("filechooserbutton1").set_filter(filefilter)
        dirlist = os.listdir("TGA") # clean out old targas
        tgalist = [tganame for tganame in dirlist if tganame.endswith(".tga")>-1]
        for tganame in tgalist:
            os.unlink("TGA\\" + tganame)
        # register imagemagick
        #os.popen(r"regedit /s imagemagick\imagemagick.reg")

    def fileselected(self, object):
        self.transparency = 1   # default to no transparency, transparency on = 2
        self.builder.get_object("transparencybutton").set_active(0)
        self.filenamedialog = self.builder.get_object("filechooserbutton1")
        self.filename = self.filenamedialog.get_filename()                           # pull filename from dialog
        if self.filename==None:
            return
        pictureupdate = gtk.gdk.PixbufAnimation(self.filename)                       # load animation into picture control
        self.builder.get_object("image1").set_from_animation(pictureupdate)
        self.filewidth = pictureupdate.get_width()                                  # get width and height from picture control
        self.fileheight = pictureupdate.get_height()
        self.fileframes = string.join(os.popen('imagemagick\identify "' + self.filename + '"').readlines()).count("[")  # count number of frames from imagemagick identify.exe
        self.builder.get_object("label3").set_label("Image info\nSize:"+str(self.filewidth)+"x"+str(self.fileheight)+"\nFrames:"+str(self.fileframes))
        # find nearest power of 2 for width and height
        self.vtfwidth = int(pow(2,round(log(self.filewidth,2))))
        self.vtfheight = int(pow(2,round(log(self.fileheight,2))))
        if self.vtfwidth > 256:     # if height or width is bigger than 256, set them to 256
            self.vtfwidth = 256
        if self.vtfheight > 256:
            self.vtfheight = 256
        self.builder.get_object("height"+str(self.vtfheight)).set_active(1)   # push the radio buttons that correspond to the size
        self.builder.get_object("width"+str(self.vtfwidth)).set_active(1)

    def sizechanged(self, object):  # buttons pressed, set values
        if self.filename==None:
            return
        if object.name.find("width")==0:
            self.vtfwidth=int(object.get_label())
        elif object.name.find("height")==0:
            self.vtfheight=int(object.get_label())
        elif object.name.find("transparency")==0:
            if object.get_active() == 1:
                self.transparency=2     # transparency on
            elif object.get_active() ==0:
                self.transparency=1     # transparency off
        
        # exception here if they try to make it bigger than the original image dimensions.
        if self.vtfwidth > int(pow(2,round(log(self.filewidth,2)))):
            self.vtfwidth = int(pow(2,round(log(self.filewidth,2))))
            if self.vtfwidth > 256:
                self.vtfwidth = 256
            self.builder.get_object("width"+str(self.vtfwidth)).set_active(1)
        if self.vtfheight > int(pow(2,round(log(self.fileheight,2)))):
            #print self.vtfheight
            self.vtfheight = int(pow(2,round(log(self.fileheight,2))))
            if self.vtfheight > 256:
                self.vtfheight = 256
            self.builder.get_object("height"+str(self.vtfheight)).set_active(1)
        
        self.vtfframes = int(round(magicnumber /(self.vtfwidth*self.vtfheight*self.transparency)))
        if self.vtfframes > self.fileframes:
            self.vtfframes = self.fileframes    # not possible to have more frames in the animation than there was in the file
        self.builder.get_object("label4").set_label("Frames in VTF: "+ str(self.vtfframes))

    def convert(self, object):
        # check if steam is running
        out = string.join(os.popen('tasklist').readlines())
        if out.find("Steam")>-1: pass # print "steam is running"
        # create exception here if the size is to big to create any frames.
        if self.vtfframes == 0:
            return
        spliceleft = 0
        splicetop = 0
        framecount = 0
        framecounter = 0
        background = ""
        splicestring = ""

        # clean out folder before putting new tgas in
        filelist = os.listdir(r"vtex\materialsrc\vgui\logos")
        for filename in filelist:
            os.unlink(r"vtex\materialsrc\vgui\logos\\"+filename)
            
        vtextext = open(r"vtex\materialsrc\vgui\logos\output.txt", "w+")
        vtextext.write('"Startframe" "0"\n')
        vtextext.write('"endframe" "'+str(self.vtfframes-1)+'"\n')
        vtextext.close()
        
        everynthframe = 1 # by default, take every frame
        if self.vtfframes < self.fileframes:
            # cut some frames out
            everynthframe = float(self.fileframes)/float(self.vtfframes)
        if self.transparency==2: background="-background transparent -bordercolor transparent " # pass this string to convert.exe if transparency is enabled
        else: background="-alpha deactivate "
        tempw = self.filewidth/float(self.vtfwidth)
        temph = self.fileheight/float(self.vtfheight)
        if temph > tempw:
            newheight = self.vtfheight
            newwidth = int(round(float(self.filewidth) * float(self.vtfheight) / float(self.fileheight)))
        else:
            newheight = int(round(float(self.fileheight) * float(self.vtfwidth) / float(self.filewidth)))
            newwidth = self.vtfwidth
        topbottomborder = int(round(self.vtfheight - newheight))
        leftrightborder = int(round(self.vtfwidth - newwidth))
        if leftrightborder % 2:   # if the border padding isn't an even number, splice an extra pixel of border in.
            spliceleft = 1
        if topbottomborder % 2:
            splicetop = 1
        if spliceleft or splicetop:
            splicestring = "-splice " + str(spliceleft) + "x" + str(splicetop)+ " "
        os.popen('imagemagick\convert +adjoin -coalesce "' + self.filename + '" TGA\output.tga') # output .tgas
        dirlist = os.listdir("TGA")
        tgalist = [tganame for tganame in dirlist if tganame.endswith(".tga")]
        natsort(tgalist)
        for tganame in tgalist:
            # process only the frames you need, speeding things up
            if tganame.find("-" + str(int(round(framecount)))) > -1:
                os.popen("imagemagick\convert -resize " + str(self.vtfwidth) + "x" + str(self.vtfheight) + " TGA\\" + tganame + " TGA\\" + tganame)
                os.popen("imagemagick\convert " + splicestring + background + "-border " + str(int(leftrightborder/2)) + "x" + str(int(topbottomborder/2)) + " TGA\\" + tganame + " TGA\\" + tganame)
                # print "convert " + splicestring + background + "-border " + str(int(leftrightborder/2)) + "x" + str(int(topbottomborder/2)) + " " + tganame + " " + tganame
                os.rename("TGA\\" + tganame,r"vtex\materialsrc\vgui\logos\output" + '%0*d' % (3, framecounter)  + ".tga")
                framecount = framecount + everynthframe
                framecounter = framecounter + 1
        # os.rename("vtex\gameinfo-css.txt","vtex\gameinfo.txt")
        out = string.join(os.popen(r'vtex\vtex.exe -nopause vtex\materialsrc\vgui\logos\output.txt').readlines()) # compile using vtex.exe
        # os.rename("vtex\gameinfo.txt","vtex\gameinfo-css.txt")
        # print out
        vtfname=os.path.basename(self.filename)
        inputbasename=vtfname.rstrip(".gif")
        vtfname=vtfname.rstrip(".gif") + ".vtf"
        #figure out game folder
        registryobj = ConnectRegistry(None,HKEY_CURRENT_USER)
        keyobj = OpenKey(registryobj, r"software\valve\steam") # 240 for CSS
        valuetuple = QueryValueEx(keyobj, "steampath")
        valuetuple2 = QueryValueEx(keyobj, "lastgamenameused")
        gamefolder = valuetuple[0].replace("/","\\") + "\\steamapps\\" + valuetuple2[0] + "\\team fortress 2\\tf"
        # HKEY_LOCAL_MACHINE\software\microsoft\windows\currentversion\uninstall\steam app 440
        # installlocation     REG_SZ  d:\games\steam\steamapps\xenoguy\team fortress 2
        # gamefolder=r"D:\games\steam\steamapps\xenoguy\team fortress 2\tf"
        
        if os.path.exists(gamefolder+"\\materials\\vgui\logos\\" + vtfname):
            if os.path.exists("vtex\\materials\\vgui\\logos\\output.vtf"):
                os.unlink(gamefolder+"\\materials\\vgui\logos\\" + vtfname)

        # create folder if it doesn't exist
        if os.path.exists(gamefolder+r"\materials\vgui\logos\ui")!=True:
            os.makedirs(gamefolder+r"\materials\vgui\logos\ui")

        # move the file into the game folder
        os.rename("vtex\\materials\\vgui\\logos\\output.vtf",gamefolder+"\\materials\\vgui\logos\\" + vtfname)

            
        vmt1 = open(gamefolder + r"\materials\vgui\logos\\" + inputbasename + ".vmt", "w+")
        vmt1.write('LightmappedGeneric\n')
        vmt1.write('{\n')
        vmt1.write('    "$basetexture"	"vgui\logos\\' + vtfname + '"\n')
        vmt1.write('    "$translucent" "1"\n')
        vmt1.write('    "$decal" "1"\n')
        vmt1.write('    "$decalscale" "0.250"\n')
        vmt1.write('}\n')
        vmt1.close()

        vmt2 = open(gamefolder + r"\materials\vgui\logos\ui\\" + inputbasename + ".vmt", "w+")
        vmt2.write('"UnlitGeneric"\n')
        vmt2.write('{\n')
        vmt2.write('    "$translucent" 1\n')
        vmt2.write('    "$basetexture"	"vgui\logos\\' + vtfname + '"\n')
        vmt2.write('    "$vertexcolor" 1\n')
        vmt2.write('    "$vertexalpha" 1\n')
        vmt2.write('    "$no_fullbright" 1\n')
        vmt2.write('    "$ignorez" 1\n')
        vmt2.write('}\n')
        vmt2.close()

        # launch explorer after installation to see how messy the game folder is
        os.spawnl(os.P_NOWAIT,"c:\windows\explorer.exe", "explorer", gamefolder + r"\materials\vgui\logos")

# show main window
frm = mainwindow()
gtk.main()

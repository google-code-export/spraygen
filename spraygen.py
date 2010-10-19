#!/usr/bin/env python
import pygtk
import gtk
import re
import os
import win32gui
import win32con
#import time
import shutil
import sys
import string
from _winreg import ConnectRegistry, OpenKey, HKEY_CURRENT_USER, QueryValueEx
from math import log

steamfolder=""
workingdir = os.getcwd()
# magicnumber = 180224 # max size for TGAs in VTF
magicnumber = 785000
vtfwidth=0
vtfheight=0
filewidth=0
fileheight=0
vtfframes=0
fileframes=0
transparency=1
filenames=[""]
filename2=""
builder = gtk.Builder()
filefilter="""Image Files\0*.gif;*.jpg;*.png;*.tga\0"""
# debug logs
#sys.stdout = open("spraygen.log", "w")
#sys.stderr = open("spraygenerr.log", "w")

def cleanup():
    # cleanup stuff here
    dirlist = os.listdir("TGA")
    tgalist = [tganame for tganame in dirlist if tganame.endswith(".tga") or tganame.endswith(".gif")]
    for tganame in tgalist:
        os.unlink("TGA\\" + tganame)
    dirlist = os.listdir("vtfcmd")
    tgalist = [tganame for tganame in dirlist if tganame.endswith(".tga")]
    for tganame in tgalist:
        os.unlink("vtfcmd\\" + tganame)
    dirlist = os.listdir("vtfcmd")
    dirlist = [fname for fname in dirlist if fname.endswith(".dds")]
    for fname in dirlist:
        os.unlink("vtfcmd\\" + fname)
    dirlist = os.listdir("vtfcmd")
    dirlist = [fname for fname in dirlist if fname.endswith(".vtf")]
    for fname in dirlist:
        os.unlink("vtfcmd\\" + fname)
    dirlist = os.listdir(r"vtex\materials\vgui\logos") # clean out old .vtfs
    filelist = [fname for fname in dirlist if fname.endswith(".vtf")]
    for fname in filelist:
        os.unlink(r"vtex\materials\vgui\logos\\" + fname)
    dirlist = os.listdir(r"vtex\materialsrc\vgui\logos") # clean out everything in materialsrc
    for fname in dirlist:
        if fname != ".svn":
            os.unlink(r"vtex\materialsrc\vgui\logos\\"+fname)

def createanimation():
    global filenames, transparency
    frame=0
    vtfwidth = 256
    vtfheight = 256
    dirlist = os.listdir("TGA")
    if os.path.exists("tga\\output.gif")!=True:
        tgalist = [tganame for tganame in dirlist if tganame.endswith(".tga") and tganame.startswith("output-")]
        for tganame in tgalist:
            os.unlink("tga\\" + tganame)
        for file in filenames:
            os.popen("imagemagick\\convert \"" + file + "\" TGA\\output-" + str(frame) + ".tga") # output .tgas
            print "imagemagick\\convert \"" + file + "\" TGA\\output-" + str(frame) + ".tga"
            print os.getcwd()
            spliceleft = 0
            splicetop = 0
            background = ""
            splicestring = ""
            temppixbuf = gtk.gdk.pixbuf_new_from_file("tga\\output-" + str(frame) + ".tga")
            filewidth = temppixbuf.get_width()
            fileheight = temppixbuf.get_height()
#            background="-background transparent -bordercolor transparent " # always import tga files as transparent
#            if transparency==2: background="-background transparent -bordercolor transparent " # pass this string to convert.exe if transparency is enabled
#            else: background="-alpha deactivate " # no transparency, no alpha channel. room for more frames.
            tempw = filewidth/float(vtfwidth)
            temph = fileheight/float(vtfheight)
            if temph > tempw:
                newheight = vtfheight
                newwidth = int(round(float(filewidth) * float(vtfheight) / float(fileheight)))
            else:
                newheight = int(round(float(fileheight) * float(vtfwidth) / float(filewidth)))
                newwidth = vtfwidth
            topbottomborder = int(round(vtfheight - newheight))
            leftrightborder = int(round(vtfwidth - newwidth))
            if leftrightborder % 2:   # if the border padding isn't an even number, splice an extra pixel of border in.
                spliceleft = 1
            if topbottomborder % 2:
                splicetop = 1
            if spliceleft or splicetop:
                splicestring = "-splice " + str(spliceleft) + "x" + str(splicetop)+ " "
            os.popen("imagemagick\\convert -resize " + str(vtfwidth) + "x" + str(vtfheight) + " tga\\output-"+str(frame)+".tga" + " tga\\output-"+str(frame)+".tga")
            os.popen("imagemagick\\convert " + splicestring + background + "-border " + str(int(leftrightborder/2)) + "x" + str(int(topbottomborder/2)) + " tga\\output-"+str(frame)+".tga tga\\output-"+str(frame)+".tga")
            frame=frame+1
        os.popen("imagemagick\\convert -delay 80 -dispose background -loop 0 TGA\\output-*.tga tga\\output.gif") # output .tgas
    animation = gtk.gdk.PixbufAnimation("tga\\output.gif")
    return animation

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
    global builder
    builder.add_from_file("spraygen.xml")
    def __init__(self):
        global steamfolder, builder
        cleanup() # clean up the junk
        # stop program when window closes
        builder.get_object("adjustment1").set_value(1)
        builder.get_object("adjustment2").set_value(1)
        dic = { "on_button1_clicked" : self.convert, "on_window1_destroy" : gtk.main_quit, "on_radiobutton1_toggled" : self.sizechanged, "on_radiobutton2_toggled" : self.sizechanged, "on_radiobutton3_toggled" : self.sizechanged, "on_radiobutton4_toggled" : self.sizechanged, "on_radiobutton5_toggled" : self.sizechanged, "on_radiobutton6_toggled" : self.sizechanged, "on_radiobutton7_toggled" : self.sizechanged, "on_radiobutton8_toggled" : self.sizechanged, "on_radiobutton9_toggled" : self.sizechanged, "on_radiobutton10_toggled" : self.sizechanged, "on_transparencybutton_toggled" : self.sizechanged, "on_importbutton_clicked" : self.importdialog, "on_animated_toggled" : self.typechanged, "on_fading_toggled" : self.typechanged, "on_spinbutton2_value_changed" : self.framechanged, "on_spinbutton1_value_changed" : self.framechanged, "on_importbutton2_clicked" : self.importdialog2}
        builder.connect_signals(dic)
        #figure out game folder
        try:
            registryobj = ConnectRegistry(None,HKEY_CURRENT_USER)
            keyobj = OpenKey(registryobj, r"software\valve\steam") 
            valuetuple = QueryValueEx(keyobj, "steampath")
            steamfolder = valuetuple[0].replace("/","\\")
        except:
            md = gtk.MessageDialog(builder.get_object("window1"), 
                gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, 
                gtk.BUTTONS_CLOSE, r"Can't find steam in the registry, assuming c:\program files\steam")
            md.run()
            md.destroy()
            steamfolder = r"c:\program files\steam"
        dirlist = os.listdir(steamfolder+"\\steamapps") #
        steamnamelist = [steamname for steamname in dirlist if os.path.isdir(steamfolder+"\\steamapps"+"\\"+steamname)]
        if "SourceMods" in steamnamelist: steamnamelist.remove("SourceMods") # remove the expected folders
        if "common" in steamnamelist: steamnamelist.remove("common") # left with a list of steam usernames, in theory
        combobox1=builder.get_object("combobox1")
        liststore = gtk.ListStore(str)
        cell = gtk.CellRendererText()
        combobox1.set_model(liststore)
        combobox1.pack_start(cell, True)
        combobox1.add_attribute(cell, 'text', 0)
        liststore1=builder.get_object("liststore1")
        for steamname in steamnamelist:
            combobox1.append_text(steamname)
        combobox1.set_active(0)

    def importdialog(self, object):
        global filefilter, filenames, workingdir
        try:
            filename, customfilter, flags=win32gui.GetOpenFileNameW(InitialDir=".", Flags=win32con.OFN_ALLOWMULTISELECT|win32con.OFN_EXPLORER, File='', DefExt='txt', Title='Import Image(s)', Filter=filefilter, FilterIndex=0)
            filenames=filename.split("\0")
            if len(filenames) > 1:
                folder=filenames[0]
                filenames.remove(folder)
                for i in range(0,len(filenames)):
                    filenames[i]=folder + "\\" + filenames[i]
        except win32gui.error:
            pass
        os.chdir(workingdir)
        self.fileselected(self)
            
    def importdialog2(self, object):
        global filefilter, filename2
        try:
            filename2, customfilter, flags=win32gui.GetOpenFileNameW(InitialDir=".", Flags=win32con.OFN_EXPLORER, File='', DefExt='txt', Title='Import Second Frame', Filter=filefilter, FilterIndex=0)
        except win32gui.error:
            pass
        os.chdir(workingdir)
        self.fileselected2(self)

    def fileselected(self, object):
        global vtfwidth, vtfheight, fileheight, filewidth, vtfframes, fileframes, filenames, builder, tgabasename, filename2
        if filenames[0]=="":
            return
        dirlist = os.listdir("TGA")
        tgalist = [tganame for tganame in dirlist if tganame.endswith(".tga") and tganame.startswith("output-") or tganame.endswith(".gif") ]
        for tganame in tgalist:
            os.unlink("tga\\" + tganame)
        filename2=""
        transparency = builder.get_object("transparencybutton").get_active()+1
        if len(filenames)<2:
            os.popen('imagemagick\convert +adjoin -coalesce "' + filenames[0] + '" TGA\output.tga') # output .tgas
        animate=builder.get_object("animated").get_active()
        fade=builder.get_object("fading").get_active()
        if len(filenames) < 2:
            pictureupdate = gtk.gdk.PixbufAnimation(filenames[0])                       # load animation into picture control
        else:
            pictureupdate = createanimation()
        tgabasename="tga\\output-"
        if filenames[0].find(".gif")==-1:
            if len(filenames)<2:
                os.rename("tga\\output.tga","tga\\output-0.tga")
        if fade:
            builder.get_object("image1").set_from_file(tgabasename+"0"+".tga")
            builder.get_object("image2").set_from_file(tgabasename+"0"+".tga")
        elif animate:
            builder.get_object("image1").set_from_animation(pictureupdate)
        filewidth = pictureupdate.get_width()                                  # get width and height from picture control
        fileheight = pictureupdate.get_height()
        if filenames[0].find(".gif")>-1:
            fileframes = string.join(os.popen('imagemagick\identify "' + filenames[0] + '"').readlines()).count("[")  # count number of frames from imagemagick identify.exe
        elif len(filenames) > 1:
            dirlist = os.listdir("TGA")
            tgalist = [tganame for tganame in dirlist if tganame.endswith(".tga") and tganame.startswith("output-")]
            fileframes=len(tgalist)
        else:
            fileframes=1
        builder.get_object("label3").set_label("Image info\nSize:"+str(filewidth)+"x"+str(fileheight)+"\nFrames:"+str(fileframes))
        # find nearest power of 2 for width and height
        vtfwidth = int(pow(2,round(log(filewidth,2))))
        vtfheight = int(pow(2,round(log(fileheight,2))))
        if vtfwidth > 512:     # if height or width is bigger than 512, set them to 512
            vtfwidth = 512
        if vtfheight > 512:
            vtfheight = 512
        builder.get_object("height"+str(vtfheight)).set_active(1)   # push the radio buttons that correspond to the size
        builder.get_object("width"+str(vtfwidth)).set_active(1)
        builder.get_object("adjustment1").set_upper(fileframes)
        builder.get_object("adjustment2").set_upper(fileframes)
        builder.get_object("adjustment1").set_value(1)
        builder.get_object("adjustment2").set_value(1)

    def fileselected2(self, object):
        global fileheight2, filewidth2, fileframes2, filename2, builder, tgabasename2, vtfframes
        if filename2=="":
            return
        dirlist = os.listdir("TGA")
        tgalist = [tganame for tganame in dirlist if tganame.endswith(".tga") and tganame.startswith("output2-")]
        for tganame in tgalist:
            os.unlink("tga\\" + tganame)
        pictureupdate = gtk.gdk.PixbufAnimation(filename2) 
        os.popen('imagemagick\convert +adjoin -coalesce "' + filename2 + '" TGA\output2.tga') # output .tgas
        if filename2.find(".gif")>-1:
            fileframes2 = string.join(os.popen('imagemagick\identify "' + filename2 + '"').readlines()).count("[")  # count number of frames from imagemagick identify.exe
        else:
            fileframes2=1
        tgabasename2="tga\\output2-"
        if filename2.find(".gif")==-1:
            os.rename("tga\\output2.tga", "tga\\output2-0.tga")
        builder.get_object("adjustment2").set_upper(fileframes2)
        builder.get_object("adjustment2").set_value(1)
        builder.get_object("image2").set_from_file(tgabasename2+"0"+".tga")
        filewidth2 = pictureupdate.get_width()                                  # get width and height from picture control
        fileheight2 = pictureupdate.get_height()

    def framechanged(self, object):
        global builder, filenames, filename2, tgabasename, tgabasename2
        frame=str(int(builder.get_object("adjustment1").get_value())-1)    
        frame2=str(int(builder.get_object("adjustment2").get_value())-1)    
        if filenames[0]:
            builder.get_object("image1").set_from_file(tgabasename+frame+".tga")
            if filename2:
                builder.get_object("image2").set_from_file(tgabasename2+frame2+".tga")
            else:
                builder.get_object("image2").set_from_file(tgabasename+frame2+".tga")

    def typechanged(self, object):
        global builder, filenames, tgabasename, tgabasename2
        animate=builder.get_object("animated").get_active()
        fade=builder.get_object("fading").get_active()
        if animate:
            builder.get_object("vbox7").hide_all()
            builder.get_object("hbox3").hide_all()
            builder.get_object("importbutton2").hide()
            if filenames[0]:
                if len(filenames) < 2:
                    pictureupdate = gtk.gdk.PixbufAnimation(filenames[0])                       # load animation into picture control
                else:
                    pictureupdate = createanimation()
                builder.get_object("image1").set_from_animation(pictureupdate)
        elif fade:
            builder.get_object("vbox7").show_all()
            builder.get_object("hbox3").show_all()
            builder.get_object("importbutton2").show()
            frame=str(int(builder.get_object("adjustment1").get_value())-1)    
            frame2=str(int(builder.get_object("adjustment2").get_value())-1)
            if filenames[0]:
                builder.get_object("image1").set_from_file(tgabasename+frame+".tga")
                if filename2:
                    builder.get_object("image2").set_from_file(tgabasename2+frame2+".tga")
                else:
                    builder.get_object("image2").set_from_file(tgabasename+frame2+".tga")
        self.sizechanged(object)


    def sizechanged(self, object):  # buttons pressed, set values
        global vtfwidth, vtfheight, fileheight, filewidth, vtfframes, fileframes, transparency, builder, filenames
        animate=builder.get_object("animated").get_active()
        fade=builder.get_object("fading").get_active()
        if filenames[0]=="":
            return
        if object.name.find("width")==0:
            vtfwidth=int(object.get_label())
        elif object.name.find("height")==0:
            vtfheight=int(object.get_label())
        transparency = builder.get_object("transparencybutton").get_active()+1
        
        # exception here if they try to make it bigger than the original image dimensions.
        if vtfwidth > int(pow(2,round(log(filewidth,2)))):
            vtfwidth = int(pow(2,round(log(filewidth,2))))
            if vtfwidth > 512:
                vtfwidth = 512
            builder.get_object("width"+str(vtfwidth)).set_active(1)
        if vtfheight > int(pow(2,round(log(fileheight,2)))):
            vtfheight = int(pow(2,round(log(fileheight,2))))
            if vtfheight > 512:
                vtfheight = 512
            builder.get_object("height"+str(vtfheight)).set_active(1)

        if fade:
            if vtfwidth > 512:
                vtfwidth = 512
                builder.get_object("width"+str(vtfwidth)).set_active(1)
            if vtfheight > 512:
                vtfheight = 512
                builder.get_object("height"+str(vtfheight)).set_active(1)

        
        vtfframes = int(round(magicnumber /(vtfwidth*vtfheight*transparency)))
        if animate:
            if vtfframes > fileframes:
                vtfframes = fileframes    # not possible to have more frames in the animation than there was in the file
        elif fade:
            vtfframes = 2
        builder.get_object("label4").set_label("Frames in VTF: "+ str(vtfframes))
        if vtfframes==0:
            builder.get_object("label4").set_label('Frames in VTF: <span foreground="red" size="x-large">' + str(vtfframes) + '</span>')

    def convert(self, object):
        global steamfolder, vtfwidth, vtfheight, fileheight, filewidth, fileheight2, filewidth2, vtfframes, fileframes, transparency, filenames, builder, workingdir, filename2, tgabasename, tgabasename2
        animate=builder.get_object("animated").get_active()
        fade=builder.get_object("fading").get_active()
        gamefolderlist=[]
        username=""
        if filenames[0]=="":
            return
        dirlist = os.listdir(r"vtex\materials\vgui\logos") # clean out old .vtfs
        filelist = [fname for fname in dirlist if fname.endswith(".vtf")]
        for fname in filelist:
            os.unlink(r"vtex\materials\vgui\logos\\" + fname)

        ## check if steam is running
        #out = string.join(os.popen('tasklist').readlines())
        #if out.lower().find("steam.exe")>-1:
        #    pass # steam is running
        #else:
        #    md = gtk.MessageDialog(builder.get_object("window1"), 
        #        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING, 
        #        gtk.BUTTONS_CLOSE, "Steam is not running, please start Steam before creating a spray")
        #    md.run()
        #    md.destroy()
        #    return
        
        # create exception here if the size is to big to create any frames.
        if vtfframes == 0: # if it has no frames, exit
            return
        spliceleft = 0
        splicetop = 0
        framecount = 0
        framecounter = 0
        background = ""
        splicestring = ""
        splicestring2 = ""
        
        vtextext = open(r"vtex\materialsrc\vgui\logos\output.txt", "w+")
        vtextext.write('"Startframe" "0"\n')
        vtextext.write('"endframe" "'+str(vtfframes-1)+'"\n')
        vtextext.close()        
        everynthframe = 1 # by default, take every frame
        if vtfframes < fileframes: # cut some frames out
            everynthframe = float(fileframes)/float(vtfframes)
        if transparency==2: background="-background transparent -bordercolor transparent " # pass this string to convert.exe if transparency is enabled
        else: background="-alpha deactivate " # no transparency, no alpha channel. room for more frames.
        tempw = filewidth/float(vtfwidth)
        temph = fileheight/float(vtfheight)
        if temph > tempw:
            newheight = vtfheight
            newwidth = int(round(float(filewidth) * float(vtfheight) / float(fileheight)))
        else:
            newheight = int(round(float(fileheight) * float(vtfwidth) / float(filewidth)))
            newwidth = vtfwidth
        topbottomborder = int(round(vtfheight - newheight))
        leftrightborder = int(round(vtfwidth - newwidth))
        if leftrightborder % 2:   # if the border padding isn't an even number, splice an extra pixel of border in.
            spliceleft = 1
        if topbottomborder % 2:
            splicetop = 1
        if spliceleft or splicetop:
            splicestring = "-splice " + str(spliceleft) + "x" + str(splicetop)+ " "
        if filename2:
            tempw = filewidth2/float(vtfwidth)
            temph = fileheight2/float(vtfheight)
            if temph > tempw:
                newheight = vtfheight
                newwidth = int(round(float(filewidth2) * float(vtfheight) / float(fileheight2)))
            else:
                newheight = int(round(float(fileheight2) * float(vtfwidth) / float(filewidth2)))
                newwidth = vtfwidth
            topbottomborder2 = int(round(vtfheight - newheight))
            leftrightborder2 = int(round(vtfwidth - newwidth))
            if leftrightborder2 % 2:   # if the border padding isn't an even number, splice an extra pixel of border in.
                spliceleft = 1
            if topbottomborder2 % 2:
                splicetop = 1
            if spliceleft or splicetop:
                splicestring2 = "-splice " + str(spliceleft) + "x" + str(splicetop)+ " "
        else:
            leftrightborder2=leftrightborder
            topbottomborder2=topbottomborder
            splicestring2=splicestring
        tgadir = "tga\\"
        dirlist = os.listdir(tgadir)
        tgalist = [tganame for tganame in dirlist if tganame.endswith(".tga")]
        natsort(tgalist) # natural sort the TGA list to get them in the right order
        vtfname=os.path.basename(filenames[0]) # name of vtf without the path
        vmtname=vtfname.rsplit(".")[0] + ".vmt"
        vtfname=vtfname.rsplit(".")[0] + ".vtf"
        if fade:
            if vtfframes == 1: # no space for 2 frames? exit.
                return
            frame=str(int(builder.get_object("adjustment1").get_value())-1)
            frame2=str(int(builder.get_object("adjustment2").get_value())-1)
            tganame1=tgabasename+frame+".tga"
            if filename2:
                tganame2=tgabasename2+frame2+".tga"
            else:
                tganame2=tgabasename+frame2+".tga"
            # generate mipmaps
            os.popen("imagemagick\convert -resize " + str(vtfwidth) + "x" + str(vtfheight) + " " + tganame1 + " vtfcmd\\output_00.tga")
            os.popen("imagemagick\convert " + splicestring + background + "-border " + str(int(leftrightborder/2)) + "x" + str(int(topbottomborder/2)) + " vtfcmd\\output_00.tga vtfcmd\\output_00.tga")
            os.popen("imagemagick\convert -resize " + str(vtfwidth) + "x" + str(vtfheight) + " " + tganame2 + " vtfcmd\\output_01.tga")
            os.popen("imagemagick\convert " + splicestring2 + background + "-border " + str(int(leftrightborder2/2)) + "x" + str(int(topbottomborder2/2)) + " vtfcmd\\output_01.tga vtfcmd\\output_01.tga")
            os.popen("imagemagick\convert -resize " + str(vtfwidth/2) + "x" + str(vtfheight/2) + " vtfcmd\\output_01.tga vtfcmd\\output_01.tga")
            for i in range(2,7):
                os.popen("imagemagick\convert -resize " + str(vtfwidth/(2**i)) + "x" + str(vtfheight/(2**i)) + " vtfcmd\\output_01.tga" + " vtfcmd\\output_0" + str(i) + ".tga")
            os.popen("vtfcmd\\nvdxt -file vtfcmd\\*.tga -dxt5 -outdir vtfcmd") # compile to dxt5 format .dds files
            os.popen("vtfcmd\\stitch vtfcmd\output") # stitch .dds files as mipmaps into one .dds texture
            os.popen('vtfcmd\\vpktoolwrap "' + workingdir + '\\vtfcmd\\output.dds"') # auto-it wrapper for quick and dirty tools, converts .dds to .vtf
            vtfpath="vtfcmd\\output.vtf"
        elif animate:
            for tganame in tgalist:
                if tganame.find("-" + str(int(round(framecount)))) > -1: # process only the frames you need, speeding things up
                    os.popen("imagemagick\convert -resize " + str(vtfwidth) + "x" + str(vtfheight) + " " + tgadir + tganame + " " + "vtex\\materialsrc\\vgui\\logos\\"  + tganame)
                    os.popen("imagemagick\convert " + splicestring + background + "-border " + str(int(leftrightborder/2)) + "x" + str(int(topbottomborder/2)) + " vtex\\materialsrc\\vgui\\logos\\" + tganame + " vtex\\materialsrc\\vgui\\logos\\" + tganame)
                    shutil.copy("vtex\\materialsrc\\vgui\\logos\\" + tganame,"vtex\\materialsrc\\vgui\\logos\\output" + '%0*d' % (3, framecounter)  + ".tga")
                    framecount = framecount + everynthframe #advance to next frame
                    framecounter = framecounter + 1
            if filenames[0].find(".gif")>-1 or len(filenames)>1:
                output = string.join(os.popen(r'vtex\vtex.exe -nopause vtex\materialsrc\vgui\logos\output.txt').readlines()) # compile using vtex.exe
            else:
                output = string.join(os.popen(r'vtex\vtex.exe -nopause vtex\materialsrc\vgui\logos\output000.tga').readlines()) # single frame
                os.rename("vtex\\materials\\vgui\\logos\output000.vtf", "vtex\\materials\\vgui\\logos\output.vtf")
            vtfpath="vtex\\materials\\vgui\\logos\\output.vtf"

        if os.path.exists(vtfpath)!=True: # if the vtf file doesn't exist, skip the rest.
            return

        username=builder.get_object("combobox1").get_active_text()
        tf2check=builder.get_object("tf2check").get_active()
        csscheck=builder.get_object("csscheck").get_active()
        l4dcheck=builder.get_object("L4Dcheck").get_active()
        l4d2check=builder.get_object("L4D2check").get_active()
        savecheck=builder.get_object("savecheck").get_active()
        line1 = re.compile(r'cl_logofile "(.*)"')
        if tf2check:
            try:
                f = open(steamfolder + "\\steamapps\\" + username + "\\team fortress 2\\tf\\cfg\\game.cfg", 'r')
                filecontents=f.read()
                f.close()
                match=line1.search(filecontents)
                if match:
                    newfilecontents=filecontents.replace(match.group(1),"materials\\vgui\\logos\\" + vtfname + '"')
                    f = open(steamfolder + "\\steamapps\\" + username + "\\team fortress 2\\tf\\cfg\\game.cfg", 'w')
                    f.write(newfilecontents)
                    f.close()
                else:
                    newfilecontents='cl_logofile "' + "materials\\vgui\\logos\\" + vtfname + '"'
                    f = open(steamfolder + "\\steamapps\\" + username + "\\team fortress 2\\tf\\cfg\\game.cfg", 'w')
                    f.write(newfilecontents)
                    f.close()
            except:
                pass
            gamefolderlist.append(steamfolder + "\\steamapps\\" + username + "\\team fortress 2\\tf\\materials\\vgui\\logos\\")
        if csscheck:
            try:
                f = open(steamfolder + "\\steamapps\\" + username + "\\counter-strike source\\cstrike\\cfg\\game.cfg", 'r')
                filecontents=f.read()
                f.close()
                match=line1.search(filecontents)
                if match:
                    newfilecontents=filecontents.replace(match.group(1),"materials\\vgui\\logos\\" + vtfname + '"')
                    f = open(steamfolder + "\\steamapps\\" + username + "\\counter-strike source\\cstrike\\cfg\\game.cfg", 'w')
                    f.write(newfilecontents)
                    f.close()
                else:
                    newfilecontents='cl_logofile "' + "materials\\vgui\\logos\\" + vtfname + '"'
                    f = open(steamfolder + "\\steamapps\\" + username + "\\counter-strike source\\cstrike\\cfg\\game.cfg", 'w')
                    f.write(newfilecontents)
                    f.close()
            except:
                pass              
            gamefolderlist.append(steamfolder + "\\steamapps\\" + username + "\\counter-strike source\\cstrike\\materials\\vgui\\logos\\")
        if l4dcheck:
            try:
                f = open(steamfolder + "\\steamapps\\common\\left 4 dead\\left4dead\\cfg\\autoexec.cfg", 'r')
                filecontents=f.read()
                f.close()
                match=line1.search(filecontents)
                if match:
                    newfilecontents=filecontents.replace(match.group(1),"materials/vgui/logos/custom/" + vtfname + '"')
                    f = open(steamfolder + "\\steamapps\\common\\left 4 dead\\left4dead\\cfg\\autoexec.cfg", 'w')
                    f.write(newfilecontents)
                    f.close()
                else:
                    newfilecontents=filecontents + "\n" + 'cl_logofile "' + "materials/vgui/logos/custom/" + vtfname + '"'
                    f = open(steamfolder + "\\steamapps\\common\\left 4 dead\\left4dead\\cfg\\autoexec.cfg", 'w')
                    f.write(newfilecontents)
                    f.close()
            except:
                newfilecontents='cl_logofile "' + "materials/vgui/logos/custom/" + vtfname + '"'
                f = open(steamfolder + "\\steamapps\\common\\left 4 dead\\left4dead\\cfg\\autoexec.cfg", 'w')
                f.write(newfilecontents)
                f.close()
            gamefolderlist.append(steamfolder + "\\steamapps\\common\\left 4 dead\\left4dead\\materials\\vgui\\logos\\custom\\")
        if l4d2check:
            try:
                f = open(steamfolder + "\\steamapps\\common\\left 4 dead 2\\left4dead2\\cfg\\autoexec.cfg", 'r')
                filecontents=f.read()
                f.close()
                match=line1.search(filecontents)
                if match:
                    newfilecontents=filecontents.replace(match.group(1),"materials/vgui/logos/custom/" + vtfname + '"')
                    f = open(steamfolder + "\\steamapps\\common\\left 4 dead 2\\left4dead2\\cfg\\autoexec.cfg", 'w')
                    f.write(newfilecontents)
                    f.close()
                else:
                    newfilecontents=filecontents + "\n" + 'cl_logofile "' + "materials/vgui/logos/custom/" + vtfname + '"'
                    f = open(steamfolder + "\\steamapps\\common\\left 4 dead 2\\left4dead2\\cfg\\autoexec.cfg", 'w')
                    f.write(newfilecontents)
                    f.close()
            except:
                newfilecontents='cl_logofile "' + "materials/vgui/logos/custom/" + vtfname + '"'
                f = open(steamfolder + "\\steamapps\\common\\left 4 dead 2\\left4dead2\\cfg\\autoexec.cfg", 'w')
                f.write(newfilecontents)
                f.close()
            gamefolderlist.append(steamfolder + "\\steamapps\\common\\left 4 dead 2\\left4dead2\\materials\\vgui\\logos\\custom\\")
    
        for gamefolder in gamefolderlist:
            if os.path.exists(gamefolder + vtfname): # if the file of the same name exists, in the game folder
                os.unlink(gamefolder + vtfname) # delete the destination file of the same name, in the game folder
    
            if os.path.exists(gamefolder + r"\ui")!=True: 
                if gamefolder.find("\\left4dead")>-1:
                    if os.path.exists(gamefolder + r"\..\ui")!=True:
                        os.makedirs(gamefolder + r"\..\ui") # create vgui folder if it doesn't exist
                else:
                    os.makedirs(gamefolder + r"\ui") # create vgui folder if it doesn't exist
    
            #output=os.popen(r'copy /y vtex\materials\vgui\logos\output.vtf "'+ gamefolder + vtfname + '"')
            shutil.copy(vtfpath,gamefolder + vtfname)
            
            #time.sleep(1)
            vmt1 = open(gamefolder + vmtname, "w+")
            vmt1.write('LightmappedGeneric\n')
            vmt1.write('{\n')
            vmt1.write('$basetexture "vgui\logos\custom/' + vtfname.rsplit(".vtf")[0] + '"\n')
            vmt1.write('$translucent 1\n')
            vmt1.write('$decal 1\n')
            vmt1.write('$decalscale "0.250"\n')
            vmt1.write('}\n')
            vmt1.close()
    
            if gamefolder.find("\\left4dead")>-1:
                vmt2 = open(gamefolder + r"\..\ui\\" + vmtname, "w+")
            else:
                vmt2 = open(gamefolder + r"\ui\\" + vmtname, "w+")
            vmt2.write('"UnlitGeneric"\n')
            vmt2.write('{\n')
            vmt2.write('    "$translucent" 1\n')
            if gamefolder.find("\\left4dead")>-1:
                vmt2.write('    "$basetexture"	"vgui\logos\custom/' + vtfname.rsplit(".vtf")[0] + '"\n')
            else:
                vmt2.write('    "$basetexture"	"vgui\logos/' + vtfname.rsplit(".vtf")[0] + '"\n')
            vmt2.write('    "$vertexcolor" 1\n')
            vmt2.write('    "$vertexalpha" 1\n')
            vmt2.write('    "$no_fullbright" 1\n')
            vmt2.write('    "$ignorez" 1\n')
            vmt2.write('}\n')
            vmt2.close()

            # launch explorer after installation to see how messy the game folder is
            os.spawnl(os.P_NOWAIT,"c:\windows\explorer.exe", "explorer", gamefolder)
        if savecheck:
            filefilter2="""Spray Files\0*.vtf\0"""
            try:
                filename, customfilter, flags=win32gui.GetSaveFileNameW(InitialDir=".", Flags=win32con.OFN_EXPLORER, File='', DefExt='txt', Title='Save Spray', Filter=filefilter2, FilterIndex=0)
                os.chdir(workingdir)
                shutil.copy(vtfpath, filename)
            except win32gui.error:
                pass
            

# show main window

frm = mainwindow()
gtk.main()

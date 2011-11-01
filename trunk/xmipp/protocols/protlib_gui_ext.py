'''
/***************************************************************************
 * Authors:     J.M. de la Rosa Trevin (jmdelarosa@cnb.csic.es)
 *
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'xmipp@cnb.csic.es'
 ***************************************************************************/
 '''

import os
from os.path import join
import Tkinter as tk

from tkSimpleDialog import Dialog
import ttk
from config_protocols import LabelBgColor, ButtonBgColor, ButtonActiveBgColor
from protlib_filesystem import getXmippPath

RESOURCES = getXmippPath('resources')
#ButtonBgColor = "LightBlue"
#ButtonActiveBgColor = "LightSkyBlue"
#ButtonSelectedColor = "DeepSkyBlue2"

Fonts = {}

def registerFont(name, **opts):
    import tkFont
    global Fonts
    Fonts[name] = tkFont.Font(**opts)

def registerCommonFonts():
    from config_protocols import FontName, FontSize
    if 'normal' not in Fonts.keys():
        registerFont('normal', family=FontName, size=FontSize)
    if 'button' not in Fonts.keys():
        registerFont('button', family=FontName, size=FontSize, weight='bold')
    if 'label' not in Fonts.keys():
        registerFont('label', family=FontName, size=FontSize+1, weight='bold')
        
def configDefaults(opts, defaults):
    for key in defaults.keys():
        if not opts.has_key(key):
            opts[key] = defaults[key]
            
def openLink(link):
    ''' Open a link in default web browser '''
    from  webbrowser import open
    open(link)
    
def changeFontSizeByDeltha(font, deltha, min=-999, max=999):
    size = font['size']
    new_size = size + deltha
    if new_size >= min and new_size <= max:
        font.configure(size=new_size)
            
def changeFontSize(font, event, min=-999, max=999):
    deltha = 2
    if event.char == '-':
        deltha = -2
    changeFontSizeByDeltha(font, deltha, min, max)

# **********************************************
# *     Following are some helper functions    *
# **********************************************

def getGeometry(win):
    ''' Return the geometry information of the windows
    It will be a tuple (width, height, x, y)
    '''
    return win.winfo_reqwidth(), win.winfo_reqheight(), win.winfo_x(), win.winfo_y()

def centerWindows(root, dim=None, refWindows=None):
    """Center a windows in the middle of the screen 
    or in the middle of other windows(refWindows param)"""
    root.update_idletasks()
    gw, gh, gx, gy = getGeometry(root)
    if refWindows:
        rw, rh, rx, ry = getGeometry(refWindows)
        x = rx + (rw - gw) / 2
        y = ry + (rh - gh) / 2 
    else:
        w = root.winfo_screenwidth()
        h = root.winfo_screenheight()
        if not dim is None:
            gw, gh = dim
        x = (w - gw) / 2
        y = (h - gh) / 2
        
    root.geometry("%dx%d+%d+%d" % (gw, gh, x, y))


'''
Taken from following forum:
http://code.activestate.com/recipes/52266-multilistbox-tkinter-widget/
This is a compound widget that gangs multiple Tk Listboxes to a single scrollbar to achieve a simple 
multi-column scrolled listbox. Most of the Listbox API is mirrored to make it act like the normal 
Listbox but with multiple values per row.
'''
class MultiListbox(tk.PanedWindow):
    """MultiListbox class for creating a Grid widget"""
    def __init__(self,master,lists):
        tk.PanedWindow.__init__(self,master,borderwidth=1,showhandle=False,sashwidth=2,sashpad=0,relief=tk.SUNKEN)
        self.lists = []
        self.columns=[]
        for l, w in lists:
            self.columns.append(l)
            frame = tk.Frame(self); frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
            tl=tk.Label(frame, text=l, borderwidth=2, relief=tk.GROOVE)
            tl.pack(fill=tk.X)
            tl.bind('<Button-1>',self.clickon)
            lb = tk.Listbox(frame, width=w, borderwidth=0, selectborderwidth=0,relief=tk.FLAT, exportselection=tk.FALSE, selectmode=tk.MULTIPLE ,bg='white')
            lb.pack(expand=tk.YES, fill=tk.BOTH)
            self.lists.append(lb)
            lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            lb.bind('<Double-Button-1>', self._doubleClick)
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
            lb.bind('<Button-3>', lambda e, s=self: s._button3(e.x, e.y))
            lb.bind('<Button-4>', lambda e, s=self: s._scroll(tk.SCROLL, 1, tk.PAGES))
            lb.bind('<Button-5>', lambda e, s=self: s._scroll(tk.SCROLL, -1, tk.PAGES))
            self.add(frame)
        sb = tk.Scrollbar(master, orient=tk.VERTICAL, command=self._scroll,borderwidth=1)
        sb.pack(fill=tk.Y,side=tk.RIGHT,expand=tk.NO)
        for l in self.lists:
            l['yscrollcommand']=sb.set
        self.add(frame)
        self.pack(expand=tk.YES,fill=tk.BOTH, side=tk.TOP)
        self.sortedBy = -1
        self.previousWheel = 0
        self.SelectCallback = None
        self.DoubleClickCallback = None
        self.AllowSort = True

    def _doubleClick(self, event=''):
        if self.DoubleClickCallback:
            self.DoubleClickCallback()

    def _select(self, y,state=16):
        row = self.lists[0].nearest(y)
        if state==16:self.selection_clear(0, tk.END)
        self.selection_set(row)
        return 'break'

    def _button2(self, x, y):
        for l in self.lists: l.scan_mark(x, y)
        return 'break'

    def _button3(self, x, y):
        #self._select(y, state)
        return 'break'
    

    def _b2motion(self, x, y):
        for l in self.lists: l.scan_dragto(x, y)        
        return 'break'


    def _scroll(self, *args):
        for l in self.lists:
            apply(l.yview, args)
        return 'break'


    def clickon(self,e):
        if self.AllowSort:
            self._sortBy(self.columns.index(e.widget['text']))


    def _sortBy(self, column):
        """ Sort by a given column. """
        if column == self.sortedBy:
            direction = -1 * self.direction
        else:
            direction = 1

        elements = self.get(0, tk.END)
        self.delete(0, tk.END)
        elements.sort(lambda x, y: self._sortAssist(column, direction, x, y))
        self.insert(tk.END, *elements)

        self.sortedBy = column
        self.direction = direction


    def _sortAssist(self, column, direction, x, y):
        c = cmp(x[column], y[column])
        if c:
            return direction * c
        else:
            return direction * cmp(x, y)

    def curselection(self):
        return self.lists[0].curselection()


    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)


    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first,last))
        if last: return apply(map, [None] + result)
        return result


    def index(self, index):
        self.lists[0].index(index)


    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1
    
    def changetext(self, index, *elements):
        for e in elements:
            for l in self.lists:
                l.itemconfig(index, text=e)        

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)


    def selection_includes(self, index):
        return self.lists[0].selection_includes(index)


    def selectedIndex(self):
        if len(self.curselection()) > 0:
            return int(self.curselection()[0])
        return -1
    
    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)
        index = self.selectedIndex()
        if self.SelectCallback:
            self.SelectCallback(index)
            
    def selection_move_up(self):
        index = self.selectedIndex() 
        if index > 0:
            self.selection_clear(0, tk.END)
            #self.selection_clear(0, END)
            self.selection_set(index - 1)
            
    def selection_move_down(self):
        index = self.selectedIndex()
        if index != -1 and index < self.size() - 1:
            self.selection_clear(0, tk.END)
            #self.selection_clear(0, END)
            self.selection_set(index + 1)


# ******************************************************************
# *     Following are implementation of some widgets extensions   *
# ****************************************************************** 

class AutoScrollbar(tk.Scrollbar):
    '''A scrollbar that hides itself if it's not needed.'''
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        tk.Scrollbar.set(self, lo, hi)
        
'''Michael Lange <klappnase (at) freakmail (dot) de>
The ToolTip class provides a flexible tooltip widget for Tkinter; it is based on IDLE's ToolTip
module which unfortunately seems to be broken (at least the version I saw).
INITIALIZATION OPTIONS:
anchor :        where the text should be positioned inside the widget, must be on of "n", "s", "e", "w", "nw" and so on;
                default is "center"
bd :            borderwidth of the widget; default is 1 (NOTE: don't use "borderwidth" here)
bg :            background color to use for the widget; default is "lightyellow" (NOTE: don't use "background")
delay :         time in ms that it takes for the widget to appear on the screen when the mouse pointer has
                entered the parent widget; default is 1500
fg :            foreground (i.e. text) color to use; default is "black" (NOTE: don't use "foreground")
follow_mouse :  if set to 1 the tooltip will follow the mouse pointer instead of being displayed
                outside of the parent widget; this may be useful if you want to use tooltips for
                large widgets like listboxes or canvases; default is 0
font :          font to use for the widget; default is system specific
justify :       how multiple lines of text will be aligned, must be "left", "right" or "center"; default is "left"
padx :          extra space added to the left and right within the widget; default is 4
pady :          extra space above and below the text; default is 2
relief :        one of "flat", "ridge", "groove", "raised", "sunken" or "solid"; default is "solid"
state :         must be "normal" or "disabled"; if set to "disabled" the tooltip will not appear; default is "normal"
text :          the text that is displayed inside the widget
textvariable :  if set to an instance of Tkinter.StringVar() the variable's value will be used as text for the widget
width :         width of the widget; the default is 0, which means that "wraplength" will be used to limit the widgets width
wraplength :    limits the number of characters in each line; default is 150

WIDGET METHODS:
configure(**opts) : change one or more of the widget's options as described above; the changes will take effect the
                    next time the tooltip shows up; NOTE: follow_mouse cannot be changed after widget initialization

Other widget methods that might be useful if you want to subclass ToolTip:
enter() :           callback when the mouse pointer enters the parent widget
leave() :           called when the mouse pointer leaves the parent widget
motion() :          is called when the mouse pointer moves inside the parent widget if follow_mouse is set to 1 and the
                    tooltip has shown up to continually update the coordinates of the tooltip window
coords() :          calculates the screen coordinates of the tooltip window
create_contents() : creates the contents of the tooltip window (by default a Tkinter.Label)
'''
# Ideas gleaned from PySol

class ToolTip:
    def __init__(self, master, text='Your text here', delay=1500, **opts):
        self.master = master
        self._opts = {'anchor':'center', 'bd':1, 'bg':'lightyellow', 'delay':delay, 'fg':'black',\
                      'follow_mouse':0, 'font':None, 'justify':'left', 'padx':4, 'pady':2,\
                      'relief':'solid', 'state':'normal', 'text':text, 'textvariable':None,\
                      'width':0, 'wraplength':150}
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1
    
    def configure(self, **opts):
        for key in opts:
            if self._opts.has_key(key):
                self._opts[key] = opts[key]
            else:    
                KeyError = 'KeyError: Unknown option: "%s"' %key
                raise KeyError
    
    ##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
    ##----events on the parent widget; override them if you want to change the widget's behavior--##
    
    def enter(self, event=None):
        self._schedule()
        
    def leave(self, event=None):
        self._unschedule()
        self._hide()
    
    def motion(self, event=None):
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))
    
    ##------the methods that do the work:---------------------------------------------------------##
    
    def _schedule(self):
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)

    def _show(self):
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = tk.Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()
    
    def _hide(self):
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()
                
    ##----these methods might be overridden in derived classes:----------------------------------##
    
    def coords(self):
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        # or we take care that the mouse pointer is always outside the tipwindow :-)
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # calculate the y coordinate:
        if self._follow_mouse:
            y = tw.winfo_pointery() + 20
            # make sure the tipwindow is never outside the screen:
            if y + twy > h:
                y = y - twy - 30
        else:
            y = self.master.winfo_rooty() + self.master.winfo_height() + 3
            if y + twy > h:
                y = self.master.winfo_rooty() - twy - 3
        # we can use the same x coord in both cases:
        x = tw.winfo_pointerx() - twx / 2
        if x < 0:
            x = 0
        elif x + twx > w:
            x = w - twx
        return x, y

    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = tk.Label(self._tipwindow, **opts)
        label.pack()

##---------demo code-----------------------------------##

class XmippButton(tk.Button):
    def __init__(self, master, text, imagePath=None, **opts):
        defaults = {'activebackground': ButtonActiveBgColor}
        defaults.update(opts)
        btnImage = None
        if imagePath:
            try:
                imgPath = join(RESOURCES, imagePath)
                btnImage = tk.PhotoImage(file=imgPath)
            except tk.TclError:
                pass
        
        if btnImage:
            tk.Button.__init__(self, master, image=btnImage, bd=0, height=28, width=28, **defaults)
            self.image = btnImage
        else:
            tk.Button.__init__(self, master, text=text, font=Fonts['button'], bg=ButtonBgColor, **defaults)

'''Implement a Listbox Dialog, it will return
the index selected in the lisbox or -1 on Cancel'''
class ListboxDialog(Dialog):
    def __init__(self, master, itemList, **kargs):
        self.list = itemList
        self.kargs = kargs
        Dialog.__init__(self, master)        
        
    def body(self, master):
        self.result = []
        self.lb = tk.Listbox(master, selectmode=tk.EXTENDED, bg="white")
        self.lb.config(**self.kargs)
        self.lb.pack(fill=tk.BOTH)
        self.lb.bind('<Double-Button-1>', self.ok)
        maxLength=0
        for item in self.list:
            self.lb.insert(tk.END, item)
            maxLength=max(maxLength,len(item))
        self.lb.config(width=maxLength+3)
        if len(self.list) > 0:
            self.lb.selection_set(0)
        return self.lb # initial focus

    def buttonbox(self):
        box = tk.Frame(self)
        w = XmippButton(box, text="OK", width=7, command=self.ok)
        w.pack(side=tk.RIGHT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        box.pack()
        
    def apply(self):
        self.result = map(int, self.lb.curselection())

    
# Tkinter Text Widget Hyperlink Manager
# taken from:
# http://effbot.org/zone/tkinter-text-hyperlink.htm
class HyperlinkManager:
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(tk.CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return
            
class XmippText(tk.Text):    
    def __init__(self, master, **options):  
        registerCommonFonts()    
        defaults = self.getDefaults()
        defaults.update(options)
        tk.Text.__init__(self, master, defaults)
        self.configureTags()

    def getDefaults(self):
        '''This should be implemented in subclasses to provide defaults'''
        return {}
    def configureTags(self):
        '''This should be implemented to create specific tags'''
        pass
    
    def addLine(self, line):
        '''Should be implemented to add a line '''
        pass
        
    def addNewline(self):
        self.insert(tk.END, '\n')
        
    def goBegin(self):
        self.see(0.0)
        
    def goEnd(self):
        self.see(tk.END)
        
    def clear(self):
        self.config(state=tk.NORMAL)
        self.delete(0.0, tk.END)

    def addText(self, text):
        self.config(state=tk.NORMAL)
        for line in text.splitlines():
            self.addLine(line)
        self.config(state=tk.DISABLED)     

'''
Implement a Text that will recognized some basic tags
<some_text> will display some_text in bold
[some_link] will display some_link as hiperlinnk
'''           
class TaggedText(XmippText):  
    def __init__(self, master, **options):  
        XmippText.__init__(self, master, **options)
        # Create regex for tags parsing
        import re
        self.regex = re.compile('((?:\[[^]]+\])|(?:<[^>]+>))')
        self.hm = HyperlinkManager(self)

    def getDefaults(self):
        return {'bg': "white", 'bd':0, 'font':Fonts['normal']}
    
    def configureTags(self):
        self.tag_config('normal', justify=tk.LEFT)
        self.tag_config('bold', justify=tk.LEFT, font=Fonts['button'])
        
        
    def getTaggedParts(self, parts):
        ''' Detect [] as links text and <> as bold text'''
        tagsDict = {'[': 'link', '<': 'bold'}
        tagged_parts = []
        for p in parts:
            if len(p) > 0:
                if p[0] in tagsDict.keys():
                    tagged_parts.append((p[1:-1], tagsDict[p[0]]))
                else:
                    tagged_parts.append((p, 'normal'))
        return tagged_parts
        
    def addLine(self, line):
        parts = self.getTaggedParts(self.regex.split(line))
        for p, t in parts:
            if t == 'link':
                def insertLink(link):
                    self.insert(tk.INSERT, link, self.hm.add(lambda: openLink(link)))
                insertLink(p)
            else:
                self.insert(tk.END, p, t)
        self.addNewline()       

'''
Implement a Text that will show file content
and handle console metacharacter for colored output
'''
class OutputText(XmippText):
    def __init__(self, master, filename, colors=True, refresh=0, goEnd=True, **opts):
        ''' colors flag indicate if try to parse color meta-characters
            refresh is the refresh timedeltha in seconds, 0 means no refresh
        '''
        self.filename = filename
        self.colors = colors
        self.refresh = refresh
        self.refreshAlarm = None
        self.lineNo = 0
        XmippText.__init__(self, master, **opts)
        self.doRefresh(refresh)

    def getDefaults(self):
        return {'bg': "black", 'fg':'white', 'bd':0, 'font':Fonts['normal'], 
                'height':30,  'width':100}
        
    def configureTags(self):
        if self.colors:
            from protlib_xmipp import colorMap
            for color in colorMap.keys():
                self.tag_config("tag_" + color, foreground=color)

    def addLine(self, line): 
        self.lineNo += 1
        if self.colors:
            from protlib_xmipp import findColor
            ctuple = findColor(line)
            self.insert(tk.END, "%05d:   " % self.lineNo,"tag_cyan")  
            if ctuple is None:
                self.insert(tk.END, line[line.rfind("\r")+1:])  
            else:
                color,idxInitColor,idxFinishColor,cleanText=ctuple
                if idxInitColor>0:
                    self.insert(tk.END, cleanText[:(idxInitColor-1)]+" ")
                self.insert(tk.END, cleanText[idxInitColor:idxFinishColor-1], "tag_" + color)
                self.insert(tk.END, cleanText[idxFinishColor:])
        else:
            self.insert(tk.END, "%05d:   " % self.lineNo)
            self.insert(tk.END, line)   
        
    def readFile(self, clear=False):
        if clear:
            self.lineNo = 0
            self.clear()
            
        self.config(state=tk.NORMAL)
        #self.clear()
        if os.path.exists(self.filename):
            textfile = open(self.filename)
            lineNo = 1
            for line in textfile:
                if lineNo > self.lineNo:
                    self.addLine(line)
                lineNo += 1
            textfile.close()
        else:
            self.addLine("File '%s' doesn't exist" % self.filename)
        self.config(state=tk.DISABLED)
        #if goEnd:
        #    self.goEnd()        
      
    def doRefresh(self, seconds):
        self.stopRefresh() #Stop pending refreshes
        self.readFile()
        if seconds:
            self.refreshAlarm = self.after(seconds*1000, self.doRefresh, seconds)
    
    def stopRefresh(self):
        if self.refreshAlarm:
            self.after_cancel(self.refreshAlarm)
            self.refreshAlarm = None

  
''' Implementation of a simple textfile viewer '''
class FileViewer(tk.Frame):
    def __init__(self, master, filelist):
        tk.Frame.__init__(self, master)
        self.searchList = None
        self.lastSearch = None
        self.refreshAlarm = None
        self.filelist = filelist
        self.taList = []
        self.fontDict = {}
        self.createWidgets()
        self.master = master
        self.addBinding()
        
    def addFileTab(self, filename):
        tab = tk.Frame(self.notebook)
        tab.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        t = OutputText(tab, filename, width=100, height=30)
        t.grid(column=0, row=0, padx=5, pady=5, sticky='nsew')
        self.taList.append(t)
        tabText = "   %s   " % os.path.basename(filename)
        self.notebook.add(tab, text=tabText)        
    
    def createWidgets(self):
        registerCommonFonts()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)        
        #Create toolbar frame
        toolbarFrame = tk.Frame(self)
        toolbarFrame.grid(column=0, row=0, padx=5, sticky='new')
        toolbarFrame.columnconfigure(0, weight=1)
        toolbarFrame.columnconfigure(1, weight=1)
        #Add the search box
        left = tk.Frame(toolbarFrame)
        left.grid(column=0, row=0, sticky='nw')
        XmippButton(left, "Open", 'folderopen.gif').grid(row=0, column=0, padx=(0, 5))
        XmippButton(left, "Save", 'save.gif').grid(row=0, column=1, padx=(0, 5))
        XmippButton(left, "Refresh", 'refresh_file.gif').grid(row=0, column=2, padx=(0, 5))
        right = tk.Frame(toolbarFrame)
        right.grid(column=1, row=0, sticky='ne')        
        self.searchVar = tk.StringVar()
        tk.Label(right, text='Search:').grid(row=0, column=3, padx=5, pady=5, )
        self.searchEntry = tk.Entry(right, textvariable=self.searchVar, bg=LabelBgColor)
        self.searchEntry.grid(row=0, column=4, sticky='ew', padx=5, pady=5)
        XmippButton(right, "Search", 'search.gif').grid(row=0, column=5, padx=(0, 5))
        
        #Create tabs frame
        tabsFrame = tk.Frame(self)
        tabsFrame.grid(column=0, row=1, padx=5, pady=5, sticky="nsew")
        tabsFrame.columnconfigure(0, weight=1)
        tabsFrame.rowconfigure(0, weight=1)
        self.notebook = ttk.Notebook(tabsFrame)  
        self.notebook.rowconfigure(0, weight=1)
        self.notebook.columnconfigure(0, weight=1)      
        for f in self.filelist:
            self.addFileTab(f)
        self.notebook.grid(column=0, row=0, sticky='nsew', padx=5, pady=5)
        
        self.searchEntry.focus_set()

    def addBinding(self):
        self.master.bind('<Control_L><Home>', lambda e: self.changePosition(1.0))
        self.master.bind('<Control_L><End>', lambda e: self.changePosition(tk.END))
        self.master.bind('<Alt_L><c>', lambda e: self.master.destroy())
        self.master.bind('<Control_L><f>', lambda e: self.searchEntry.focus_set())
        self.master.bind('<Return>', lambda e: self.findText())
        self.master.bind('<Control_L><n>', lambda e: self.findText())
        self.master.bind('<Control_L><p>', lambda e: self.findText(-1))
        self.master.bind('<Alt_L><plus>', self.changeFont)
        self.master.bind('<Alt_L><minus>', self.changeFont)
    
    def selectedText(self):
        return self.taList[self.notebook.index(self.notebook.select())]
    
    def changeFont(self, event=""):
        for font in self.fontDict.values():
            changeFontSize(font, event)
              
    def refreshOutput(self):
        if self.refreshAlarm:
            self.after_cancel(self.refreshAlarm)
            self.refreshAlarm = None
        self.selectedText().readFile()
        #self.refreshAlarm = self.after(2000, self.refreshOutput)
        
    def changePosition(self, index):
        self.selectedText().see(index)
        
    def findText(self, direction=1):
        text = self.selectedText()
        str = self.searchVar.get()
        if str is None or str != self.lastSearch:
            self.buildSearchList(text, str)
            self.lastSearch = str
        else:
            self.nextSearchIndex(text, direction)
        self.searchEntry.focus_set()
        
    def buildSearchList(self, text, str):
        text.tag_remove('found', '1.0', tk.END)
        list = []
        if str:
            idx = '1.0'
            while True:
                idx = text.search(str, idx, nocase=1, stopindex=tk.END)
                if not idx: break
                lastidx = '%s+%dc' % (idx, len(str))
                text.tag_add('found', idx, lastidx)
                list.append((idx, lastidx))
                idx = lastidx
        text.tag_config('found', foreground='white', background='blue')
        #Set class variables
        self.searchList = list
        self.currentIndex = -1
        self.nextSearchIndex(text) #select first element
    
    def nextSearchIndex(self, text, direction=1):
        #use direction=-1 to go backward
        text.tag_remove('found_current', '1.0', tk.END)
        if len(self.searchList)==0:
            return
        self.currentIndex = (self.currentIndex + direction) % len(self.searchList)
        idx, lastidx = self.searchList[self.currentIndex]
        text.tag_config('found_current', foreground='yellow', background='red')
        text.tag_add('found_current', idx, lastidx)
        text.see(idx)
  
if __name__ == '__main__':
    import sys
    root = tk.Tk()
    root.withdraw()
    root.title("View files")
    l = FileViewer(root, filelist=sys.argv[1:])
    l.pack(side=tk.TOP, fill=tk.BOTH)
    centerWindows(root)
    root.deiconify()
    root.mainloop()               
            
'''Implementation of our own dialog to display messages'''
class ShowDialog(Dialog):
    def __init__(self, master, title, msg, type):
        self.msg = msg
        self.type = type
        Dialog.__init__(self, master, title)        
        
    def body(self, master):
        try:
            from protlib_filesystem import getXmippPath
            self.image = tk.PhotoImage(file=join(getXmippPath('resources'), self.type + '.gif'))
        except tk.TclError:
            self.image = None
        self.result = []
        self.frame = tk.Frame(master, bg="white", bd=2)
        self.text = TaggedText(self.frame)
        # Insert image
        if self.image:
            self.label = tk.Label(self.frame, image=self.image, bg='white', bd=0)
            self.label.pack(side=tk.LEFT, anchor=tk.N)
        # Insert lines of text
        mylines = self.msg.splitlines()
        m = 0
        for l in mylines:
            m = max(m, len(l))
            self.text.addLine(l)
        m = min(m + 5, 80)
        self.text.config(height=len(mylines)+3, width=m-7)
        self.text.addNewline()
        self.text.config(state=tk.DISABLED)
        self.text.pack()
        self.frame.pack()
        
    def buttonbox(self):
        box = tk.Frame(self)    
        self.btnNo = XmippButton(box, text="Ok", width=7, command=self.cancel)
        self.btnNo.pack(side=tk.LEFT, padx=5, pady=5, anchor='e')
        box.pack()
        self.bind("<Return>", self.cancel)
        self.bind("<Escape>", self.cancel)

'''Implementation of our own version of Yes/No dialog'''
class YesNoDialog(ShowDialog):
    def __init__(self, master, title, msg, DefaultNo=True):
        self.defaultNo = DefaultNo
        self.result = False
        ShowDialog.__init__(self, master, title, msg, 'warning')        
        
    def buttonbox(self):
        box = tk.Frame(self)    
        self.btnYes = XmippButton(box, text="Yes", width=7, command=self.ok)
        self.btnYes.pack(side=tk.LEFT, padx=5, pady=5, anchor='e')
        self.btnNo = XmippButton(box, text="No", width=7, command=self.cancel)
        self.btnNo.pack(side=tk.LEFT, padx=5, pady=5, anchor='e')
        box.pack()
        if self.defaultNo:
            self.btnNo.focus_set()
        else: 
            self.btnYes.focus_set()
        self.bind("<Return>", self.handleReturn)
        self.bind("<Escape>", self.cancel)
        self.bind("<Left>", lambda e: self.btnYes.focus_set())
        self.bind("<Right>", lambda e: self.btnNo.focus_set())

    def apply(self):
        self.result = True
        
    def handleReturn(self, event=None):
        w = self.focus_get()
        if w is self.btnYes:
            self.ok()
        else:
            self.cancel()

''' Functions to display dialogs '''
def askYesNo(title, msg, parent):
    d = YesNoDialog(parent, title, msg)
    return d.result

def showInfo(title, msg, parent):
    ShowDialog(parent, title, msg, 'info')

def showWarning(title, msg, parent):
    ShowDialog(parent, title, msg, 'warning')
    
def showError(title, msg, parent):
    ShowDialog(parent, title, msg, 'error')

        
'''Implement an Entry that support autocomplete on <Tab>
it will have a list of choices, that will be updated
through an update function everytime the entry get the focus'''
class AutoCompleteEntry(tk.Entry):
    def __init__(self, master, **opts):
        tk.Entry.__init__(self, master, **opts)
        
    def setBuildListFunction(self, listFunc, refreshOnTab=False):
        self.listFunc = listFunc
        self.refreshOnTab = refreshOnTab
        self.bind('<FocusIn>', self.refreshList)
        self.bind('<Tab>', self.handle_tab)   
        
    def refreshList(self, event=None):
        self.choices = self.listFunc()
        
    def handle_tab(self, event):
        if self.refreshOnTab:
            self.choices = self.listFunc()
        hits = []
        for e in self.choices:
            if e.startswith(self.get()):
                hits.append(e)
        prefix = os.path.commonprefix(hits)
        if len(prefix):
            self.delete(0, tk.END)
            self.insert(0, prefix)
            self.select_clear()
            self.icursor(tk.END)
        return "break"
    

'''**************  Implementation of Xmipp Browser *************'''
# Some helper functions for the browser
def showj(filename, mode):
    from protlib_utils import runImageJPlugin
    runImageJPlugin("512m", "XmippBrowser.txt", "-i %s --mode %s" % (filename, mode), batchMode=True)
    
def chimera(filename):
    os.system('chimera spider:%s &' % filename)
    
def fileInfo(browser):
    from protlib_utils import pretty_date
    msg =  "<size:> %d bytes\n" % browser.stat.st_size
    msg += "<modified:> %s\n" % pretty_date(int(browser.stat.st_mtime))
    return msg
    
# Event handlers for each action and each type of file
def defaultOnClick(filename, browser):
    import stat
    mode = browser.stat.st_mode
    if stat.S_ISDIR(mode):
        img = 'folder.png'
        msg = "<%d items>\n" % len(browser.tree.get_children(filename))
    else:
        img = 'file.png'
        msg = ''
    fn = join(RESOURCES, img)
    browser.updatePreview(fn)
    return msg
        
def defaultFillMenu(filename, browser):
    return False

def defaultOnDoubleClick(filename, browser):
    pass

def textFillMenu(filename, browser):
    menu = browser.menu
    menu.add_command(label="Open as Text", command=lambda: showFileViewer(filename, [filename], browser.parent))
    menu.add_separator()
    menu.add_command(label="Delete file", command=None)
    return True

def textOnDoubleClick(filename, browser):
    filelist = [filename]
    loglist = ['.log', '.out', '.err']
    prefix, ext = os.path.splitext(filename)
    if ext in loglist:
        filelist = [prefix + ext for ext in loglist ]
    showFileViewer(filename, filelist, browser.parent)

def getMdString(filename, browser):
    from xmipp import MetaData, MDL_IMAGE, label2Str
    md = MetaData(filename)
    labels = md.getActiveLabels()
    msg =  "  <%d items>\n" % md.size()
    msg += "  <labels:>" + ''.join(["\n   - %s" % label2Str(l) for l in labels])
    if MDL_IMAGE in labels:
        browser.updatePreview(md.getValue(MDL_IMAGE, md.firstObject()))
    return msg
    
def mdOnClick(filename, browser):
    if '@' not in filename:
        import xmipp
        msg = "<Metadata File>\n"
        blocks = xmipp.getBlocksInMetaDataFile(filename)
        nblocks = len(blocks)
        if nblocks <= 1:
            msg += "  <single block>\n" + getMdString(filename, browser)
        else:
            msg += "  <%d blocks:>" % nblocks + ''.join(["\n  - %s" % b for b in blocks])
            # Insert blocks in metadata as independent items
            if len(browser.tree.get_children(filename)) == 0:
                fm = browser.managers['md']
                from os.path import basename
                
                for b in blocks:
                    bname = "%s@%s" % (b, filename)                    
                    btext = "%s@%s" % (b, basename(filename))
                    browser.tree.insert(filename, 'end', bname, text=btext, image=fm.image)
    else:
        msg = "<Metadata Block>\n" + getMdString(filename, browser)
    return msg
        
def mdFillMenu( filename, browser):
    menu = browser.menu
    menu.add_command(label="Open", command=lambda: showj(filename, 'metadata'))
    menu.add_command(label="Open as Images table", command=lambda:showj(filename, 'gallery'))
    menu.add_command(label="Open as ImageJ gallery", command=lambda: showj(filename, 'image'))
    menu.add_command(label="Open as Text", command=lambda: showFileViewer(filename, [filename], browser.parent))
    menu.add_separator()
    menu.add_command(label="Delete file", command=None) 
    return True

def mdOnDoubleClick(filename, browser):
    showj(filename, 'metadata')

def imgOnClick(filename, browser):
    import xmipp
    x, y, z, n = xmipp.SingleImgSize(filename)
    dimMsg = "<Image>\n  <dimensions:> %(x)d x %(y)d" 
    expMsg = "Columns x Rows "
    if z > 1: 
        dimMsg += " x %(z)d"
        expMsg += " x Slices"
    if n > 1:
        dimMsg += " x %(n)d" 
        expMsg += " x Objects"
    browser.updatePreview(filename)
    return (dimMsg + "\n" + expMsg) % locals()
        
def imgFillMenu( filename, browser):
    menu = browser.menu
    menu.add_command(label="Open", command=lambda: showj(filename, 'image'))
    menu.add_separator()
    menu.add_command(label="Delete file", command=None) 
    return True

def imgOnDoubleClick(filename, browser):
    showj(filename, 'image')

def stackFillMenu( filename, browser):
    menu = browser.menu
    menu.add_command(label="Open", command=lambda: showj(filename, 'gallery'))
    menu.add_command(label="Open in ImageJ", command=lambda:showj(filename, 'image'))
    menu.add_command(label="Open as MetaData", command=lambda: showj(filename, 'metadata'))
    menu.add_separator()
    menu.add_command(label="Delete file", command=None) 
    return True

def stackOnDoubleClick(filename, browser):
    showj(filename, 'gallery')
        
def volFillMenu( filename, browser):
    menu = browser.menu
    menu.add_command(label="Open", command=lambda: showj(filename, 'gallery'))
    menu.add_command(label="Open as ImageJ gallery", command=lambda:showj(filename, 'image'))
    menu.add_command(label="Open with Chimera", command=lambda:chimera(filename))
    menu.add_separator()
    menu.add_command(label="Delete file", command=None) 
    return True

def volOnDoubleClick(filename, browser):
    showj(filename, 'gallery')
    
class FileManager():
    ''' Class to handle different types of files '''
    def __init__(self, **attributes):
        for k, v in attributes.iteritems():
            setattr(self, k, v)

class XmippBrowser():
    ''' seltype is the selection type, it could be:
        - file -> only allow files selection
        - folder -> only allow folder selection
        - both -> allow any selection
        - none -> doesn't select, only explore
        selmode is the selection mode, it could be:
        - browse -> only single file selection
        - extended -> multiple file selection
    '''
    def __init__(self, initialDir='.', parent=None, root=None, seltype="both", selmode="browse", filter=None, previewDim=128):
        self.seltype = seltype
        self.selmode = selmode
        self.dir = initialDir
        self.pattern = filter
        self.selectedFiles = None
        self.dim = previewDim
        
    def addFileManager(self, key, icon, extensions, 
                       fillMenu=defaultFillMenu, 
                       onClick=defaultOnClick,
                       onDoubleClick=defaultOnDoubleClick):
        img = tk.PhotoImage(file=join(RESOURCES, icon))
        fm = FileManager(key=key, icon=icon, image=img, 
                         fillMenu=fillMenu,
                         onClick=onClick,
                         onDoubleClick=onDoubleClick)
        self.managers[key] = fm
        for ext in extensions:
            self.extSet[ext] = fm
        
    def createFileManagers(self):
        self.managers = {}
        self.extSet = {}
        addFm = self.addFileManager
        addFm('md', 'md.gif', ['.xmd', '.sel', '.doc', '.ctfparam', '.ctfdat'], 
                            mdFillMenu, mdOnClick, mdOnDoubleClick)
        addFm('stk', 'stack.gif', ['.stk', '.mrcs'],
                            stackFillMenu, imgOnClick, stackOnDoubleClick)
        addFm('img', 'image.gif', ['.xmp', '.tif', '.spi', '.mrc'],
                            imgFillMenu, imgOnClick, imgOnDoubleClick)
        addFm('vol', 'vol.gif', ['.vol'], 
                            volFillMenu, imgOnClick, volOnDoubleClick)
        addFm('text', 'fileopen.gif', ['.txt', '.c', '.h', '.cpp', '.java', '.sh'],
              textFillMenu, defaultOnClick, textOnDoubleClick)
        addFm('pyfile', 'python_file.gif', ['.py'],textFillMenu, defaultOnClick, textOnDoubleClick)
        addFm('out', 'out.gif', ['.out'],textFillMenu, defaultOnClick, textOnDoubleClick)
        addFm('err', 'err.gif', ['.err'],textFillMenu, defaultOnClick, textOnDoubleClick)
        addFm('log', 'log.gif', ['.log'],textFillMenu, defaultOnClick, textOnDoubleClick)
        addFm('folder', 'folderopen.gif', [])
        addFm('default', 'generic_file.gif', [])
        
    def createDetailsTop(self, parent):
        self.detailstop = ttk.Frame(parent)
        self.detailstop.rowconfigure(0, weight=1)
        self.detailstop.columnconfigure(0, weight=1)
        return self.detailstop
    
    def createDetailsBottom(self, parent):
        # Add details text
        self.text = TaggedText(parent, width=20, height=5)
        self.text.grid(column=0, row=1, sticky="nwes")
        return self.text
            
    def createGUI(self, root=None, title='', parent=None):
        if root:
            self.root = root
        else:
            self.root = tk.Tk()
        self.parent = parent   
        self.createFileManagers()
        self.root.withdraw()
        self.root.columnconfigure(0, weight=1, minsize=100)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.minsize(600, 400)
        titleStr = "Xmipp Browser"
        if len(title):
            titleStr += " - %s" % title
        elif self.seltype != 'none':
            titleStr += " - Choose " + self.seltype
        self.root.title(titleStr)

        #Create frame for tree
        frame = ttk.Frame(self.root, padding="3 3 12 12")
        frame.grid(column=0, row=0, sticky="nwes")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        tree = ttk.Treeview(frame, selectmode=self.selmode)#, columns=('items'))
        tree.grid(column=0, row=0, sticky="nwes")
        self.tree = tree
        # List for hidden tree items, (parent, item)
        self.hidden = []
        #tree.column('items', width=60, anchor='e')
        #tree.heading('items', text='Items')

        #Create frame for details
        details = ttk.Frame(self.root, padding="3 3 3 3")
        details.grid(column=1, row=0, sticky="nwes")
        details.columnconfigure(0, weight=1)
        details.rowconfigure(0, weight=1, minsize=100)  
        details.rowconfigure(1, weight=1)
        top = self.createDetailsTop(details)
        if top:
            top.grid(column=0, row=0, sticky="nwes")
        bottom = self.createDetailsBottom(details)
        if bottom:
            bottom.grid(column=0, row=1, sticky="nwes")
        self.details = details
        
        #Create bottom frame with search bar and buttons
        bottomFrame = ttk.Frame(self.root, padding="3 3 0 0")
        bottomFrame.grid(column=0, row=1, columnspan=2, sticky='ew')
        bottomFrame.columnconfigure(0, weight=1)
        bottomFrame.columnconfigure(1, weight=1)
        #Create filter frame
        filterFrame = ttk.Frame(bottomFrame)
        filterFrame.grid(column=0, row=0, sticky='ew')
        ttk.Label(filterFrame, text="Filter").pack(side=tk.LEFT,padx=2)
        self.filterVar = tk.StringVar()
        if self.pattern:
            self.filterVar.set(self.pattern)
        filterEntry = ttk.Entry(filterFrame, width=25, textvariable=self.filterVar)
        filterEntry.pack(side=tk.LEFT,padx=2)
        self.btnFilter = XmippButton(filterFrame, "Search", 'search.gif', command=self.filterResults)
        filterEntry.bind('<Return>', self.filterResults)
        self.btnFilter.pack(side=tk.LEFT, padx=2)
        #Create buttons frame
        buttonsFrame = ttk.Frame(bottomFrame)
        buttonsFrame.grid(column=1, row=0, sticky='e')
        if self.seltype != 'none':
            self.btnOk = XmippButton(buttonsFrame, "Select", command=self.selectFiles)
            self.btnOk.pack(side=tk.LEFT,padx=(0, 5))
            cancelName = "Cancel"
        else:
            cancelName = "Close"
        self.btnCancel = XmippButton(buttonsFrame, cancelName, command=self.close)
        self.btnCancel.pack(side=tk.LEFT, padx=(0, 10))
        
        #create menu
        # create a popup menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Open", command=self.onDoubleClick)
        self.menu.add_command(label="Redo", command=self.onDoubleClick) 
             
        # add bindings
        tree.bind("<Double-1>", self.onDoubleClick)
        tree.bind("<Return>", self.onDoubleClick)
        tree.bind("<Button-3>", self.onRightClick)
        self.root.bind("<Button-1>", self.onClick)
        self.root.bind("<Key>", self.onKeyPress)
        
        #Create xmipp image to show preview
        import xmipp
        self.canvas = None
        self.image = xmipp.Image()
        self.lastitem = None
        #Create a dictionary with extensions and icon type
        self.insertFiles(self.dir)
        #Filter result, if pattern no provided, all files will be listed
        self.filterResults()
        
    def showGUI(self, loop=True):        
        centerWindows(self.root, refWindows=self.parent)
        self.root.deiconify()
        if loop:
            self.root.mainloop()

    def insertElement(self, root, elem, isFolder=False):
        if root == self.dir: parent = ''
        else: parent = root
        fm = None
        if isFolder:
            fm = self.managers['folder']
        else:
            ext = os.path.splitext(elem)[1]
            if self.extSet.has_key(ext):
                fm = self.extSet[ext]
            else:
                fm = self.managers['default']
        self.tree.insert(parent, 'end', join(root, elem), text=elem, image=fm.image)

    def insertFiles(self, path):
        for root, dirs, files in os.walk(path, followlinks=True):
            if dirs:
                dirs.sort()
            if files:
                files.sort()
            for d in dirs: 
                self.insertElement(root, d, True)
            for f in files:
                if not (f.startswith('.') or f.endswith('~') or f.endswith('.pyc')):
                    self.insertElement(root, f)
    
    def unpostMenu(self):
        self.menu.unpost()
        
    def getSelection(self):
        selection = self.tree.selection()
        item = fm = None
        if len(selection) == 1:
            item = selection[0]
            ext = os.path.splitext(item)[1]
            if self.extSet.has_key(ext):
                fm = self.extSet[ext]
            else:
                fm = self.managers['default']
        return (item, fm)
        
    #Functions for handling events
    def onDoubleClick(self, e=None):
        item, fm = self.getSelection()
        if fm:
            fm.onDoubleClick(item, self)
    
    def onRightClick(self, e):
        item, fm = self.getSelection()
        if fm:
            self.menu.delete(0, tk.END)
            if fm.fillMenu(item, self):
                self.menu.post(e.x_root, e.y_root)

    def onClick(self, e):
        self.unpostMenu()
        item, fm = self.getSelection()
        if fm:
            msg = ""
            if os.path.exists(item):
                self.lastitem = item
                import stat
                self.stat = os.stat(item)
                msg = fileInfo(self)
                if self.seltype != "none":
                    correct = (stat.S_ISDIR(self.stat.st_mode) and self.seltype != 'file') or self.seltype != 'folder'
                    if correct:
                        self.btnOk.config(state=tk.NORMAL)
                    else:
                        self.btnOk.config(state=tk.DISABLED)
            msg += fm.onClick(item, self)  
            if self.text:
                self.text.clear()
                self.text.addText(msg) 
        return item
        
    def onKeyPress(self, e):
        self.unpostMenu()

    def createPreviewCanvas(self):
        from protlib_gui_figure import createImageFigure
        self.canvas, figure, self.figureimg = createImageFigure(self.detailstop, self.dim)
    
    def updatePreview(self, filename):
        if not self.canvas:
            self.createPreviewCanvas()            
        if not filename.endswith('.png'):
            #Read image data through Xmipp
            self.image.readPreview(filename, self.dim)
            from protlib_xmipp import getImageData
            Z = getImageData(self.image)
        else:
            from protlib_gui_figure import getPngData
            Z = getPngData(filename)
        self.figureimg.set_array(Z)
        self.figureimg.autoscale()
        self.canvas.show()   
    
    def filterResults(self, e=None):
        self.pattern = self.filterVar.get().split()
        self.clearFilter()
        
        if len(self.pattern):
            self.filterTreeItems('', self.tree.get_children())
    
    def clearFilter(self):
        for parent, child, index in self.hidden:
            self.tree.reattach(child, parent, index)
            self.hideItem(child)
        del self.hidden[:]      

    def hideItem(self, item):
        while item != '':
            self.tree.item(item, open=False)
            item = self.tree.parent(item)
         
    def matchPattern(self, item):
        i = os.path.basename(item)
        from fnmatch import fnmatch
        for p in self.pattern:
            if fnmatch(i, p):
                return True
        return False
    
    def filterTreeItems(self, parent, items):
        for i in items:
            if os.path.isdir(i):
                self.filterTreeItems(i, self.tree.get_children(i))
            elif self.matchPattern(i):
                self.tree.see(i)
                self.filterTreeItems(i, self.tree.get_children(i))
            else:
                index = self.tree.index(i)
                self.tree.detach(i)
                self.hidden.append((parent, i, index))
        
    def close(self, e=None):
        self.root.destroy()
        
    def selectFiles(self, e=None):
        self.selectedFiles = self.tree.selection()
        self.root.destroy()

class XmippSlider(ttk.Frame):
    ''' Create a personalized frame that contains label, slider and label value
        it also keeps a variable with the value
    '''
    def __init__(self, master, label, from_=0, to=100, value=50, callback=None):
        self.var = tk.DoubleVar()
        self.var.set(float(value))
        ttk.Frame.__init__(self, master)
        ttk.Label(self, text=label).pack(side=tk.LEFT, padx=2, pady=2, anchor='s')
        self.slider = tk.Scale(self, from_=from_, to=to, variable=self.var, 
                                bigincrement=0.01, resolution=0.01, orient=tk.HORIZONTAL)
        if callback:
            self.var.trace('w', callback)
        self.slider.pack(side=tk.LEFT, padx=2)        
        
            
class XmippBrowserCTF(XmippBrowser):
    ''' This subclass is specific for CTF preview
    '''
    def __init__(self, **args):
        if args.has_key('downsampling'):
            self.downsampling = args['downsampling']
            del args['downsampling']
        else:
            self.downsampling = '1'
        if args.has_key('freqs'):
            self.freqs = args['freqs']
            del args['freqs']
        else:
            self.freqs = None
        XmippBrowser.__init__(self, **args)
        
    def createDetailsTop(self, parent):
        XmippBrowser.createDetailsTop(self, parent)
        self.createPreviewCanvas()
        ttk.Label(self.detailstop, text="Micrograph").grid(row=1, column=0)
        ttk.Label(self.detailstop, text="PSD").grid(row=1, column=1)
        self.frame2 = ttk.Frame(self.detailstop, padding="3 3 3 3")
        self.detailstop.columnconfigure(1, weight=1)
        self.frame2.grid(column=1, row=0, sticky='nsew', padx=5)
        self.frame2.columnconfigure(0, weight=1)
        self.frame2.rowconfigure(0, weight=1)
        self.root.minsize(800, 400)        
        
        return self.detailstop
    
    def createDetailsBottom(self, parent):
        self.text = None
        frame = ttk.Frame(parent)
        ttk.Label(frame, text="Downsampling").pack(side=tk.LEFT,padx=2)
        self.downsamplingVar = tk.StringVar()
        self.downsamplingVar.set(self.downsampling)
        downsamplingEntry = ttk.Entry(frame, width=10, textvariable=self.downsamplingVar)
        downsamplingEntry.pack(side=tk.LEFT,padx=2)
        self.btnTest = XmippButton(frame, "Preview", command=self.calculatePSD)
        downsamplingEntry.bind('<Return>', self.calculatePSD)
        self.btnTest.pack(side=tk.LEFT, padx=2)
        if self.freqs:
            self.freqFrame = ttk.LabelFrame(frame, text="Frequencies", padding="5 5 5 5")
            self.freqFrame.pack()
            lf = self.freqs[0]
            hf = self.freqs[1]
            self.lf = XmippSlider(self.freqFrame, 'Low freq: ', from_=0, to=0.5, value=lf,
                                  callback=lambda a, b, c:self.updateFreqRing())
            self.lf.pack(padx=2, pady=2)
            self.hf = XmippSlider(self.freqFrame, 'High freq: ', from_=0, to=0.5, value=hf,
                                  callback=lambda a, b, c:self.updateFreqRing())
            self.hf.pack(padx=2, pady=2)
            from protlib_gui_figure import PsdFigure
            self.psdFig = PsdFigure(self.frame2, self.dim, lf, hf, dpi=64)
            self.updatePSD(Z=None)
        return frame
    
    def calculatePSD(self, e=None):
        #Read image data through Xmipp
        if self.lastitem:
            from xmipp import fastEstimateEnhancedPSD, Image
            from protlib_xmipp import getImageData
            self.image = fastEstimateEnhancedPSD(self.lastitem, float(self.downsamplingVar.get()), self.dim)
            #Following for fast testing
            #self.image = Image()
            #self.image.readPreview(self.lastitem, self.dim)
            Z = getImageData(self.image)
            self.updatePSD(Z)            
        else:
            showWarning("Operation failed","Select an image to preview", self.root)
    
    def updateFreqRing(self):
        self.psdFig.updateFreq(self.lf.var.get(), self.hf.var.get())
        
    def updatePSD(self, Z=None, state=tk.NORMAL):
        if not Z is None:
            state=tk.NORMAL
        else:
            state=tk.DISABLED
            
        if self.freqs:
            self.psdFig.updateData(Z)
            self.lf.slider.config(state=state)
            self.hf.slider.config(state=state)
            
        
    def selectFiles(self, e=None):
        self.selectedFiles = [self.downsamplingVar.get()]
        if self.freqs:
            self.selectedFiles += [self.lf.var.get(), self.hf.var.get()]
        self.root.destroy() 
        
    def onClick(self, e):
        current = self.lastitem
        XmippBrowser.onClick(self, e)
        if current != self.lastitem:
            self.updatePSD(Z=None)
        
    
'''Show Xmipp Browser and return selected files'''
def showBrowseDialog(path='.', title='', parent=None, main=False, browser=XmippBrowser, **args):
    if main:
        root = tk.Tk()
    else:
        root = tk.Toplevel()
    #root.grab_set()
    args['initialDir'] = path
    xb = browser(**args)
    xb.createGUI(root, title, parent)
    xb.showGUI(loop=False)
    root.wait_window(root)
    return xb.selectedFiles

def showFileViewer(title, filelist, parent=None, main=False):
    if main:
        root = tk.Tk()
    else:
        root = tk.Toplevel()
    root.withdraw()
    root.title(title)
    l = FileViewer(root, filelist)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    l.grid(column=0, row=0, sticky='nsew')
    centerWindows(root, refWindows=parent)
    root.deiconify()
    root.mainloop()
    
   
    
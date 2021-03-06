# -*- coding: utf-8 -*-
from Tkinter import *
from time import ctime
import os
import re
import GetZealerVideo as soup
import GetMyDrivers as mnews
from UseProxy import *

class GetResource(object):
    def __init__(self):
        self.win = Tk()

        self.l1 = StringVar(self.win)
        self.msg = ""
        self.frame = Frame(width=800, height=600, bg='white')
        self.frame.propagate(False)
        self.frame.pack()

        self.scroll = Scrollbar(self.frame)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(self.frame, selectbackground='blue', font='12', heigh=550, width=750, yscrollcommand=self.scroll.set,
                               xscrollcommand=self.scroll.set)
        self.listbox.pack(side=TOP, fill=BOTH)
        self.listbox.bind('<Double-1>', self.get_select)

        self.frame2 = Frame(width=800, height=50, bg='white')
        self.frame2.propagate(False)
        self.frame2.pack()
        Button(self.frame2, text=u'Get Zealer', command=self.zealer_video).pack(expand=YES)

        Button(self.frame2, text=u'Get Mydrivers', command=self.my_drivers).pack(expand=YES)

    def my_drivers(self):
        print 'start get at:', ctime()
        self.listbox.delete(0, END)
        self.get_m = mnews.GetMyDrivers()
        proxy_set = UseProxy()
        for l in self.get_m.split_content(proxy_set):
            s = str(l).decode('utf-8')
            try:
                self.listbox.insert(END, re.findall(r'(?<=href=").+?(?=">)', s)[0]+"\r\n")
                self.listbox.insert(END, re.findall(r'(?<=>).+?(?=<)', s)[0]+"\r\n")
                self.listbox.update()
            except IndexError:
                pass
        print 'get done at:', ctime()

    def zealer_video(self):
        print 'start get at:', ctime()
        self.listbox.delete(0, END)
        self.getz = soup.GetZealerVideo()
        proxy_set = UseProxy()
        for l in self.getz.split_content(proxy_set):
            self.listbox.insert(END, l+"\r\n")
            self.listbox.update()
        print 'get done at:', ctime()

    def get_select(self, ev=None):
        self.listbox.config(selectbackground='red')
        print self.listbox.curselection()
        self.check = self.listbox.get(self.listbox.curselection())
        if self.check:
            if re.match('http', self.check):
                os.startfile(self.check)

def main():
    d = GetResource()
    mainloop()

if __name__ == '__main__':
    main()
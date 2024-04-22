#from tkinter import *
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

import socket
import logging
from datetime import datetime

from app.classes import Protocol

def addr2int(ip, port: int):
    binport = bin(port)[2:].rjust(16, "0")
    binip = "".join([bin(int(i))[2:].rjust(8, "0") for i in ip.split(".")])
    return int(binip + binport, 2)

def int2addr(num):
    num = bin(num)[2:].rjust(48, "0")
    print(num)
    num = [
        str(int(i, 2))
        for i in [num[0:8], num[8:16], num[16:24], num[24:32], num[32:48]]
    ]
    return ".".join(num[0:4]), int(num[4])

def tree2str(tree, indent_width=4):
    def _tree2str(start, parent, tree, grandpa=None, indent=""):
        outstr = ""
        if parent != start:
            if grandpa is None:  # Ask grandpa kids!
                outstr += parent
            else:
                outstr += parent + "\n"
        if parent not in tree:
            return outstr
        for child in tree[parent][:-1]:
            outstr += indent + "├" + "─" * indent_width
            outstr += _tree2str(start, child, tree, parent, indent + "│" + " " * 4)
        
        child = tree[parent][-1]
        outstr += indent + "└" + "─" * indent_width
        outstr += _tree2str(start, child, tree, parent, indent + " " * 5) + "\n"  # 4 -> 5
        
        return outstr
    
    outstr = "00000000: Root"
    parent = outstr
    outstr += "\n" + _tree2str(outstr, parent, tree)        
    return outstr

#def loop():
#    updateForm()
#    root.after(500, loop)

#def updateForm():
#    if s == 0 :
#        lblInfo["text"] = f"Нет соединения с интернетом."
#    else :    
#        now = datetime.now()
#        current_time = now.strftime("%H:%M:%S")

#        lblInfo["text"] = f"Локальный IP: {socket.gethostbyname(socket.gethostname())} Внешний IP: {s.getPublic_ip()} \n Соединений: {len(Protocol.getSessions())} Время: {current_time}"
#        inputYourNumber.delete(0, END)
#        inputYourNumber.insert(0, f"{addr2int(s.public_ip,int(s.public_port))}")
#    lblChat["text"] = tree2str(Protocol.get_tree())
    
#def btn_NewNumber():
#    global s
#    port = Protocol.randomport()
#    s = 0
#    try:
#        s = Protocol.Session(port)    
#    except Exception as e:
#        s = 0
#    updateForm()

#def btn_Connect():
#    if inputPeerNumber.get() != "" :
#        i, p = int2addr(int(inputPeerNumber.get()))
#        s.make_connection(i, p)
#        Protocol.sessions.append(s)
#        s.backlife_cycle(1)
#        updateForm()

#def btn_Message():
#    if inputMessage.get() != "" :
#        Protocol.data_add(inputMessage.get()) 
#        updateForm()

#def root_onClosing():
#    Protocol.data_dump()
#    root.destroy()

#def _onKeyRelease(event):
#    ctrl  = (event.state & 0x4) != 0
#    if event.keycode==88 and  ctrl and event.keysym.lower() != "x":
#        event.widget.event_generate("<<Cut>>")
#    if event.keycode==86 and  ctrl and event.keysym.lower() != "v":
#        event.widget.event_generate("<<Paste>>")
#    if event.keycode==67 and  ctrl and event.keysym.lower() != "c":
#        event.widget.event_generate("<<Copy>>")



# Глобальные настройки
Window.size = (250, 200)
Window.clearcolor = (0/255, 0/255, 0/255, 1)
Window.title = "Connector"

if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG, filename="main.log")
    logging.info("Hello world!")
    logging.getLogger().setLevel(logging.DEBUG)
    logging.warning(f"Logger for DEBUG is running!")

    Protocol.data_load()

#    root = Tk()
#    root.title("Connector")
#    root.bind_all("<Key>", _onKeyRelease, "+")
#    root.protocol("WM_DELETE_WINDOW", root_onClosing)
#    root.after_idle(loop)

#    lblInfo = Label(root)
#    lblInfo.place(relwidth=1, relheight=0.1)
#
#    frameTop = Frame(root)
#    frameTop.place(rely=0.1 ,relwidth=1, relheight=0.2) 
#
#    lblYourNumber = Label(frameTop, text='Твой номер:')
#    lblYourNumber.place(relwidth=0.3, relheight=0.5)
#
#    inputYourNumber = Entry(frameTop, font=("Courier New", 10))
#    inputYourNumber.place(relx=0.3, relwidth=0.5, relheight=0.5)
#
#    btnNewNumber = Button(frameTop, text='*', command=btn_NewNumber)
#    btnNewNumber.place(relx=0.8, relwidth=0.2, relheight=0.5)
#
#    inputPeerNumber = Entry(frameTop, font=("Courier New", 10))
#    inputPeerNumber.place(rely=0.5, relwidth=0.8, relheight=0.5)
#
#    btnConnect = Button(frameTop, text='Подкл.', command=btn_Connect)
#    btnConnect.place(rely=0.5, relx=0.8, relwidth=0.2, relheight=0.5)
#
#    frameCentr = Frame(root)
#    frameCentr.place(rely=0.3, relwidth=1, relheight=0.6)
#
#    lblChat = Label(frameCentr, bg='red', anchor="nw", justify="left", font=("Courier New", 8))
#    lblChat.place(relheight=1, relwidth=1)
#
#    frameBottom = Frame(root)
#    frameBottom.place(rely=0.9, relwidth=1, relheight=0.1)
#
#    inputMessage = Entry(frameBottom)
#    inputMessage.place(relwidth=0.8, relheight=1)
#
#    btnMessage = Button(frameBottom, text='Отпр.', command=btn_Message)
#    btnMessage.place(relx=0.8, relwidth=0.2, relheight=1)
#
#    btn_NewNumber()
#
#    root.mainloop()
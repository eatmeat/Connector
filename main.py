#from tkinter import *
from kivy.app import App
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock

import socket
import logging
from datetime import datetime

from app.classes import Protocol

# Глобальные настройки
Window.size = (500, 700)
Window.clearcolor = (0/255, 0/255, 0/255, 1)
Window.title = "Connector"

class ConnectorApp(App):
    
    def __init__(self):
        super().__init__()
        self.lblInfo = Label()
        self.inputYourNumber = TextInput(hint_text='Твой номер:', multiline=False)
        self.inputPeerNumber = TextInput(hint_text='Hомер второго:', multiline=False) 
        self.inputMessage = TextInput(hint_text='Сообщение:', multiline=False) 
        self.lblChat = Label()
        self.s = 0

    def addr2int(self, ip, port: int):
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

    def tree2str(self, tree, indent_width=4):
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
    
    def updateForm(self, *args):
        if self.s == 0 :
            self.lblInfo.text = f"Нет соединения с интернетом."
            self.inputYourNumber.text = "none"
        else :    
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")

            self.lblInfo.text = f"Локальный IP: {socket.gethostbyname(socket.gethostname())} Внешний IP: {self.s.getPublic_ip()} \n Соединений: {len(Protocol.getSessions())} Время: {current_time}"
            self.inputYourNumber.text = f"{self.addr2int(self.s.public_ip,int(self.s.public_port))}"
        self.lblChat.text = self.tree2str(Protocol.get_tree())
    
    def btnNewNumberOnClick(self, *args):
        port = Protocol.randomport()
        self.s = 0
        try:
            self.s = Protocol.Session(port)    
        except Exception as e:
            self.s = 0
        self.updateForm()
    
    def btnConnectOnClick(self, *args):
        if self.inputPeerNumber.text != "" :
            i, p = self.int2addr(int(self.inputPeerNumber.text))
            self.s.make_connection(i, p)
            Protocol.sessions.append(self.s)
            self.s.backlife_cycle(1)
            self.updateForm()
    
    def btnSendOnClick(self, *args):
        if self.inputMessage.text != "" :
            Protocol.data_add(self.inputMessage.text) 
            self.updateForm()

    def build(self):
        self.btnNewNumberOnClick()
        
        btnNewNumber = Button(text='*')
        btnNewNumber.bind(on_press=self.btnNewNumberOnClick)

        btnConnect = Button(text='Con')
        btnConnect.bind(on_press=self.btnConnectOnClick)

        btnSend = Button(text='Send')
        btnSend.bind(on_press=self.btnSendOnClick)

        boxYourNumber = BoxLayout()
        boxYourNumber.add_widget(Label(text='Твой номер:'))
        boxYourNumber.add_widget(self.inputYourNumber)
        boxYourNumber.add_widget(btnNewNumber)

        boxPeerNumber = BoxLayout()
        boxPeerNumber.add_widget(self.inputPeerNumber)
        boxPeerNumber.add_widget(btnConnect)

        boxChat = BoxLayout()
        boxChat.add_widget(self.lblChat)
        
        boxSendMessage = BoxLayout()
        boxSendMessage.add_widget(self.inputMessage)
        boxSendMessage.add_widget(btnSend)

        box = BoxLayout(orientation='vertical')
        box.add_widget(self.lblInfo)
        box.add_widget(boxYourNumber)
        box.add_widget(boxPeerNumber)
        box.add_widget(boxChat)
        box.add_widget(boxSendMessage)

        Clock.schedule_interval(self.updateForm, 1)
        return box

if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG, filename="main.log")
    logging.info("Hello world!")
    logging.getLogger().setLevel(logging.DEBUG)
    logging.warning(f"Logger for DEBUG is running!")

    Protocol.data_load()
    ConnectorApp().run() 
    Protocol.data_dump()


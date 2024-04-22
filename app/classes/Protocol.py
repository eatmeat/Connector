import logging
import socket
import time
import threading
import random
import logging
import json
import re
import hashlib

missed_messages = (set())                               # Storage for hashes of required but missed messages (to request them later)
_alreadyused = set()

pool = []                                               # Pool for commands to any session (like RQD to initiate data update)
data = {}
sessions = []

def getSessions():
    global sessions
    return sessions

def randomport():
    global _alreadyused
    p = random.randint(16000, 65535)
    while p in _alreadyused:
        p = random.randint(16000, 65535)
    _alreadyused.update({p})
    return p

def aegis(f):
    def wr():
        while 1:
            try:
                f()
                break
            except Exception as e:
                logging.critical(e)
    return wr

def dat_to_bytes(diction: dict) -> bytes:
    return json.dumps(diction).encode("cp866")

def bytes_to_dat(byte: bytes) -> dict:
    return json.loads(byte.decode("cp866"))

def get_tree():
    global data
    data = data.copy()
    data.update({"00000000": "Root"})
    data.update({"ffffffff": "Lost"})
    dct = {}

    for key, message in data.items():
        if message not in dct:
            dct.update({message: []})

    for key, message in data.items():
        rep = [i[1:] for i in re.findall("@+[a-z0-9]{8}", message)]

        if len(rep) > 0:
            rep = rep[0]
        else:
            rep = "00000000"

        if rep not in data:
            rep = "ffffffff"
        if data[rep] in dct:
            dct[data[rep]].append(message)
        else:
            pass
            # dct.update({rep+": "+data[rep]:[key+": "+message]})
    # print(dct)
    dct["Root"].remove("Root")
    for k, v in list(dct.items()).copy():
        if v == []:
            dct.pop(k)
    return dct

def checksum(b):
    return hashlib.blake2s(b, digest_size=4).hexdigest()

def data_add(item):
    data.update({checksum(item.encode("cp866")): item})

def data_dump():
    with open("chat-savefile.json", "w") as f:
        json.dump(data, f)

def data_load():
    global data
    try:
        with open("chat-savefile.json", "r") as f:
            data = json.load(f)
    except:
        logging.error(f"No save file exists! New one created")
        with open(f"chat-savefile.json", "w") as f:
            json.dump({}, f)

class Session:
    def __init__(self, port):
        # self.prefix="IDL"
        self.immortal = False
        self.local_port = port
        for i in range(10):
            
            host="stun.ekiga.net"
            logging.debug(f"STUN request via {host}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("0.0.0.0", self.local_port))
            sock.setblocking(0)
            server = socket.gethostbyname(host)
            work = True
            while work:
                sock.sendto(b"\x00\x01\x00\x00!\x12\xa4B\xd6\x85y\xb8\x11\x030\x06xi\xdfB", (server, 3478), )
                for i in range(20):
                    try:
                        ans, addr = sock.recvfrom(2048)
                        work = False
                        break
                    except:
                        time.sleep(0.01)
            sock.close()
        
        self.public_ip = socket.inet_ntoa(ans[28:32])
        self.public_port = int.from_bytes(ans[26:28], byteorder="big")
        self.socket = None
        self.client = None
        self.thread = None
        logging.info(f'"{self.public_ip}",{self.public_port}')
    
    def getPublic_ip(self):
       return self.public_ip 

    def make_connection(self, ip, port, timeout=10):
        logging.debug(f"Start waiting for handshake with {ip}:{port}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.local_port))
        sock.setblocking(0)
        while True:
            sock.sendto(b"Con. Request!", (ip, port))
            time.sleep(2)
            try:
                ans, addr = sock.recvfrom(9999)
                sock.sendto(b"Con. Request!", (ip, port))
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(("0.0.0.0", self.local_port))
                sock.setblocking(0)
                self.client = (ip, port)
                self.socket = sock
                logging.debug(f"Hole with {self.client} punched!")
                break
            except Exception as e:
                assert timeout > 0
                timeout -= 1
                logging.debug(f"No handshake with {ip}:{port} yet...")

    def backlife_cycle(self, freq=1):
        global sessions
        if self.immortal:
            logging.warning(f"{self.client} session beacame immortal")
            self.life_cycle = aegis(self.life_cycle)
        th = threading.Thread(target=self.life_cycle, args=(freq,))
        th.start()
        self.thread = th
        logging.warning(f"Session with {self.client} stabilized!")
        # sessions.append(self)

    def life_cycle(self, freq=1):
        global data
        global sessions
        global pool
        c = 0
        while 1:
            if len(pool):
                pref = pool.pop(0)
            else:
                pref = b"KPL"

            self.socket.sendto(pref, self.client)  # Keep-alive
            time.sleep(max(random.gauss(1 / freq, 3), 0))

            while True:
                try:
                    ans, reply_addr = self.socket.recvfrom(9999)
                    logging.debug(
                        f"{self.client[0]}: Recieved {ans[:3].decode('cp866')} from {reply_addr}: {ans}"
                    )
                except:
                    break

                if ans[:3] == b"KPL":
                    c += 1
                    if c % 10 == 0:
                        logging.debug(
                            f"{self.client[0]}: Requesting Datagram     {c//10}"
                        )
                        self.socket.sendto(b"RQD", self.client)
                        c += 1
                    elif c % 33 == 0:
                        logging.debug(
                            f"{self.client[0]}: Requesting Session List {c//33}"
                        )
                        self.socket.sendto(b"RQS", self.client)
                        c += 1

                # ----------------------------------------Hashes (keys) sync (disabled now)----------------------------------------
                elif ans[:3] == b"RQH":
                    logging.debug(f"{self.client[0]}: Sending hashes")
                    self.socket.sendto(
                        b"HAS" + dat_to_bytes(list(data.keys())), self.client
                    )

                elif ans[:3] == b"HAS":
                    missed_messages.update(
                        set(bytes_to_dat(ans[3:])) - set(data.keys())
                    )

                # ----------------------------------------Data sync----------------------------------------
                elif ans[:3] == b"RQD":
                    if ans[3:] != b"":
                        logging.debug(f"{self.client[0]}: Sending specific datagram")
                        n = {}
                        r = set(bytes_to_dat(ans[3:]))
                        for i in r:
                            if i in data:
                                n.update({i: data[i]})
                        logging.debug(f"{self.client[0]}: Sending {n}")
                        self.socket.sendto(b"DAT" + dat_to_bytes(n), self.client)
                    else:
                        logging.debug(f"{self.client[0]}: Sending datagram")
                        self.socket.sendto(b"DAT" + dat_to_bytes(data), self.client)

                elif ans[:3] == b"DAT":
                    data.update(bytes_to_dat(ans[3:]))

                # ----------------------------------------IP list sync-------------------------------------
                elif ans[:3] == b"RQS":
                    logging.debug(f"{self.client[0]}: Sending Session List")
                    sess = [i.client[0] if i.client else None for i in sessions]
                    sess = set(sess)
                    sess = sess - {None}
                    sess = list(sess)
                    sess.remove(self.client[0])
                    self.socket.sendto(b"SES" + dat_to_bytes(sess), self.client)

                elif ans[:3] == b"SES":
                    sess = [i.client[0] if i.client else None for i in sessions]
                    sess = set(sess)
                    sess = sess - {None}
                    logging.debug(
                        f"{self.client[0]}: My sessions: {sess} Recieved: {set(bytes_to_dat(ans[3:]))} New: {list(set(bytes_to_dat(ans[3:]))-sess)}"
                    )
                    uncon = list(set(bytes_to_dat(ans[3:])) - sess)
                    if not uncon:
                        continue
                    adr = random.choice(uncon)
                    s = Session()
                    sessions.append(s)
                    self.socket.sendto(
                        b"HOP"
                        + socket.inet_aton(adr)
                        + b"CON"
                        + s.public_ip.encode("cp866")
                        + b":"
                        + str(s.public_port).encode("cp866"),
                        self.client,
                    )
                # ----------------------------------------HOP Tracking-------------------------------------
                elif ans[:3] == b"HOP":
                    sess = [i.client[0] if i.client else None for i in sessions]

                    ip = socket.inet_ntoa(ans[3:7])
                    if ip in sess:
                        s = sessions[sess.index(ip)]
                        s.socket.sendto(ans[7:], s.client)

                elif ans[:3] == b"CON":
                    s = Session()
                    adr, prt = ans[3:].decode("cp866").split(":")
                    self.socket.sendto(
                        b"HOP"
                        + socket.inet_aton(adr)
                        + b"RDY"
                        + prt.encode("cp866")
                        + b":"
                        + s.public_ip.encode("cp866")
                        + b":"
                        + str(s.public_port).encode("cp866"),
                        self.client,
                    )
                    try:
                        s.make_connection(adr, int(prt))
                        s.backlife_cycle(1)
                        sessions.append(s)
                    except:
                        logging.error(f"{self.client[0]}: Connect initiation timeout!")

                elif ans[:3] == b"RDY":
                    myprt, adr, prt = ans[3:].decode("cp866").split(":")
                    sess = [i.public_port for i in sessions]

                    if int(myprt) in sess:
                        s = sessions[sess.index(int(myprt))]
                        try:
                            s.make_connection(adr, int(prt))
                            s.backlife_cycle(1)
                        except:
                            logging.error(
                                f"{self.client[0]}: Connect stabilization timeout!"
                            )
                            sessions.remove(s)

                # ----------------------------------------Disabled Trash-----------------------------------
                elif ans[:3] == b"TRK":
                    adr, prt = ans[3:].decode("cp866").split(",")
                    sess = [i.client[0] for i in sessions]
                    sess.remove(self.client[0])
                    s = sessions[sess.index(adr)]

                    s.socket.sendto(
                        b"CN0"
                        + f"{self.client[0].encode('cp866')}:{prt.encode('cp866')}",
                        s.client,
                    )

                elif ans[:3] == b"CN0":
                    s = Session()
                    self.socket.sendto(
                        b"CN1"
                        + f"{s.public_ip.encode('cp866')}:{str(s.public_port).encode('cp866')}",
                        self.client,
                    )
                    adr, prt = ans[3:].decode("cp866").split(":")
                    s.make_connection(adr, int(prt))
                    sessions.append(s)
                elif ans[:3] == b"TRK":
                    pass
                else:
                    logging.warning(f"{self.client[0]}: Malformed! !!!{ans}!!!")
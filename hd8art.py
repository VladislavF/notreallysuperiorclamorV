#!/usr/bin/env python3

import argparse
import socket
import os
import time

#parser = argparse.ArgumentParser()
#parser.add_argument("lot_id", type=int)
#parser.add_argument("filename")
#parser.add_argument("--host", default="localhost")
#parser.add_argument("--psd-port", type=int, default=52002)
#parser.add_argument("--file-port", type=int, default=52004)
#args = parser.parse_args()

sendReal = False
hostname = "localhost"
fakefile = "HD8a.png"
realfile = "real/HD8a.png"
psd_port = 52003
file_port = 52004
lot_id = 7
lot_id_real = 7


while True:
    if not sendReal:
        print("sending fake file")
        with open(fakefile, "rb") as f:
            data = f.read()
        basename = os.path.basename(fakefile)

        command = f"streamfile|{lot_id}|{len(data)}|{basename}\n".encode()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, file_port))
        s.send(command)
        s.send(data)
        s.close()

        command = f"lot{lot_id}\n".encode()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, psd_port))
        s.send(command)
        s.close()
        sendReal = True
        time.sleep(5*60) 
    else:
        print("sending real file")
        with open(realfile, "rb") as f:
            data = f.read()
        basename = os.path.basename(realfile)

        command = f"streamfile|{lot_id_real}|{len(data)}|{basename}\n".encode()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, file_port))
        s.send(command)
        s.send(data)
        s.close()

        command = f"lot{lot_id_real}\n".encode()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, psd_port))
        s.send(command)
        s.close()
        sendReal = False
        time.sleep(1*60) 

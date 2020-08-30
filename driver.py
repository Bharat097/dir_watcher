import os
import time
import sys
from watcher import Watcher


if __name__ == "__main__":

    #  path = "D:\\Bharat - Cisco DCN\\Bharat\\Assign\\Asign"
    path = input("Enter path to monitor for txt files. \n(Leave blank to monitor current dir) \n").strip()
    todecode_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "todecode")

    txt_watcher = Watcher(action="store_to_zip", path=path, file_type=["txt"])
    todecode_watcher = Watcher(action="filter_zip", path=todecode_path, file_type=["zip"])
    txt_watcher.daemon = True
    todecode_watcher.daemon = True

    try:
        txt_watcher.start()
        time.sleep(1)
        todecode_watcher.start()
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped Manually..")

from __future__ import print_function
import os
import threading
import time
from zipper import Zipper
from pii_filter import ToDecoder


class Watcher(threading.Thread):
    """Monitor the specified path for specified type of files."""

    def __init__(self, action, path=None, file_type=[]):
        """Initialize the parameters."""
        super(Watcher, self).__init__()
        self.files = []
        self.file_handler_threads = []
        self.mtimes = {}
        self._monitor_continously = True
        self.current_dir = os.path.abspath(os.path.dirname(__file__))
        self.path = path or self.current_dir
        self.files_to_monitor = file_type
        self.action = action

    def run(self):
        """Invoke run_monitor function."""
        self.run_monitor()

    def run_monitor(self):
        """Monitor path continuously."""
        try:
            while self._monitor_continously:
                self.update_file_list()
                self.monitor_once()
                # print("Active Threads: {}".format(threading.activeCount()))
                # for each in self.file_handler_threads:
                #     each.join()
                # print("clearing list..")
                # self.file_handler_threads.clear()
                time.sleep(1)
        except Exception as e:
            print("Exception occured: {}".format(e))

    def monitor_once(self):
        """Monitor path once and detect the new/changed files."""
        # print(self.files)
        for f in self.files:
            file_path = os.path.join(self.path, f)
            try:
                mtime = os.stat(file_path).st_mtime_ns
            except FileNotFoundError:
                self.files.remove(f)
                continue
            except OSError:
                time.sleep(1)
                mtime = os.stat(f).st_mtime_ns

            if f not in self.mtimes.keys():
                self.mtimes[f] = mtime
                print("New file detected: {}".format(f))
                self.handle_new_file(file_name=f)
                continue

            if mtime > self.mtimes[f]:
                print("File changed: {}".format(f))
                self.mtimes[f] = mtime

    def update_file_list(self):
        """Create the unique list of specified file type."""
        _, _, files = next(os.walk(self.path), (self.path, [], []))
        new_files = []
        for file in files:
            ext = file.rsplit(".", 1)[1]
            if ext in self.files_to_monitor and file not in self.files:
                new_files.append(file)
        self.files += new_files

    def handle_new_file(self, file_name):
        """Take appropriate action on detection of new file."""
        if self.action == "store_to_zip":
            obj = Zipper(self.path, file_name)
        elif self.action == "filter_zip":
            obj = ToDecoder(file_name)
        # self.file_handler_threads.append(obj)
        obj.daemon = True
        obj.start()
        obj.join()

from __future__ import print_function
import os
import threading
import time
from datetime import datetime
import zipfile


class Zipper(threading.Thread):
    """Create the zip file and store it in todecode folder."""

    def __init__(self, dir_path, file_name):
        """Initialize."""
        super(Zipper, self).__init__()
        self.current_dir = os.path.abspath(os.path.dirname(__file__))
        self.file_name = file_name
        self.dir_path = dir_path
        self.file = os.path.join(self.dir_path, file_name)
        self.dest_path = os.path.join(self.current_dir, "todecode")
        if not os.path.exists(self.dest_path):
            os.mkdir(self.dest_path)
        self.remove_files()

    def run(self):
        """Start creating zip."""
        print("Zipper: processing file: {}".format(self.file_name))
        self.create_zip()
        print("Zipper: processed file: {}".format(self.file_name))

    def remove_files(self):
        """Remove file from todecode folder if any."""
        flag = False
        _, _, files = next(os.walk(self.dest_path), (self.dest_path, [], []))
        for each in files:
            file_path = os.path.join(self.dest_path, each)
            try:
                os.remove(file_path)
            except PermissionError:
                flag = True
                print("Zipper: File: {} is being used by another process".format(each))
        #  Will not create and store the zip in todecode folder until all files are removed.
        if flag:
            self.remove_files()

    def create_zip(self):
        """Create  and store the zip file to todecode folder with "%Y_%m_%d_%H_%M_%S_%f_%p" naming convention."""
        current_time = datetime.now()
        zip_file_name = "{}.zip".format(current_time.strftime("%Y_%m_%d_%H_%M_%S_%f_%p").lower())
        zip_file_pwd = str(current_time.timestamp())
        z = os.path.join(self.dest_path, zip_file_name)

        with zipfile.ZipFile(z, "w") as file:
            file.setpassword(bytes(zip_file_pwd, 'utf-8'))
            file.write(self.file, arcname=self.file_name)

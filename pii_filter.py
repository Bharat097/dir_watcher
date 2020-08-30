from __future__ import print_function
import os
import threading
import time
from datetime import datetime
import zipfile
import re

date             = re.compile('(?:(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?\s+(?:of\s+)?(?:jan\.?|january|feb\.?|february|mar\.?|march|apr\.?|april|may|jun\.?|june|jul\.?|july|aug\.?|august|sep\.?|september|oct\.?|october|nov\.?|november|dec\.?|december)|(?:jan\.?|january|feb\.?|february|mar\.?|march|apr\.?|april|may|jun\.?|june|jul\.?|july|aug\.?|august|sep\.?|september|oct\.?|october|nov\.?|november|dec\.?|december)\s+(?<!\:)(?<!\:\d)[0-3]?\d(?:st|nd|rd|th)?)(?:\,)?\s*(?:\d{4})?|[0-3]?\d[-\./][0-3]?\d[-\./]\d{2,4}', re.IGNORECASE)
time             = re.compile('\d{1,2}:\d{2} ?(?:[ap]\.?m\.?)?|\d[ap]\.?m\.?', re.IGNORECASE)
phone            = re.compile('''((?:(?<![\d-])(?:\+?\d{1,3}[-.\s*]?)?(?:\(?\d{3}\)?[-\s*]?)?\d{3}[-\s*]?\d{4}(?![\d-]))|(?:(?<![\d-])(?:(?:\(\+?\d{2}\))|(?:\+?\d{2}))\s*\d{2}\s*\d{3}\s*\d{4}(?![\d-])))''')
phones_with_exts = re.compile('((?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*(?:[2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|(?:[2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[-]\s*)?)?(?:[2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[-]\s*)?(?:[0-9]{4})(?:\s*(?:#|x?|ext?|extension)\s*(?:\d+)?))', re.IGNORECASE)
email            = re.compile("([a-z0-9!#$%&'*+=?^_`{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
ip               = re.compile('(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', re.IGNORECASE)
ipv6             = re.compile('\s*(?!.*::.*::)(?:(?!:)|:(?=:))(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)){6}(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)[0-9a-f]{0,4}(?:(?<=::)|(?<!:)|(?<=:)(?<!::):)|(?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)){3})\s*', re.VERBOSE|re.IGNORECASE|re.DOTALL)
credit_card      = re.compile('((?:(?:\\d{4}[- ]?){3}\\d{4}|\\d{15,16}))(?![\\d])')
btc_address      = re.compile('(?<![a-km-zA-HJ-NP-Z0-9])[13][a-km-zA-HJ-NP-Z0-9]{26,33}(?![a-km-zA-HJ-NP-Z0-9])')
street_address   = re.compile('\d{1,4} [\w\s]{1,20}(?:street|st|avenue|ave|road|rd|highway|hwy|square|sq|trail|trl|drive|dr|court|ct|park|parkway|pkwy|circle|cir|boulevard|blvd)\W?(?=\s|$)', re.IGNORECASE)
zip_code         = re.compile(r'\b\d{5}(?:[-\s]\d{4})?\b')
po_box           = re.compile(r'P\.? ?O\.? Box \d+', re.IGNORECASE)
ssn              = re.compile('(?!000|666|333)0*(?:[0-6][0-9][0-9]|[0-7][0-6][0-9]|[0-7][0-7][0-2])[- ](?!00)[0-9]{2}[- ](?!0000)[0-9]{4}')
from_prefix      = re.compile(r'(?i)[\\|/]+(?:Users|User|Group|Name)[\\|/]+([^\\|/]*)')
drive            = re.compile(r'(?i)(.:)[\\|/]+')

pii_list = {
    "dates"            : date,
    "times"            : time,
    "credit_cards"     : credit_card,
    "phones"           : phone,
    "phones_with_exts" : phones_with_exts,
    "emails"           : email,
    "ips"              : ip,
    "ipv6s"            : ipv6,
    "btc_addresses"    : btc_address,
    "street_addresses" : street_address,
    "zip_codes"        : zip_code,
    "po_boxes"         : po_box,
    "ssn_number"       : ssn,
    "from_prefix"      : from_prefix,
    "drive"            : drive,
}


class ToDecoder(threading.Thread):
    """Unzip file from todecode and perform pii filtering."""

    def __init__(self, file_name):
        """Initialize."""
        super(ToDecoder, self).__init__()
        self.file = file_name
        self.current_dir = os.path.abspath(os.path.dirname(__file__))
        self.file_path = os.path.join(self.current_dir, "todecode", self.file)
        self.filtered_data = ""
        self.filtered_dir = os.path.join(self.current_dir, "filtered")
        self.in_filename = None
        if not os.path.exists(self.filtered_dir):
            os.mkdir(self.filtered_dir)

    def run(self):
        """Read the zip and store it to filtered folder."""
        print("Filter: processing file: {}".format(self.file))
        try:
            self.read_zip_and_pii()
            self.write_filtered()
            print("Filter: processed file: {}".format(self.file))
        except FileNotFoundError:
            print("Filter: File: {} is deleted.".format(self.file))
        except PermissionError:
            print("Filter: File: {} is being used by another process.".format(self.file))

    def read_zip_and_pii(self):
        """Extract, read and perform pii on the specified zip."""
        pwd = bytes(self.get_password(), "utf-8")
        with zipfile.ZipFile(self.file_path, 'r') as myzip:
            self.in_filename = myzip.namelist()[-1]
            with myzip.open(name=self.in_filename, mode='r', pwd=pwd) as text_file:
                while True:
                    line = text_file.readline().rstrip(b'\n').decode()
                    if not line:
                        break
                    self.perform_pii(line)

    def get_password(self):
        """Extract and return password from the file name."""
        file_time_list = self.file.rstrip(".zip").split("_")
        dt = "/".join(file_time_list[:3])
        tm = ":".join(file_time_list[3:6])
        micro_sec = file_time_list[-2]
        am_pm = file_time_list[-1]
        file_time = "{} {}.{}{}".format(dt, tm, micro_sec, am_pm.upper())
        date_time_obj = datetime.strptime(file_time, "%Y/%m/%d %H:%M:%S.%f%p")
        epoch_time = date_time_obj.timestamp()
        return str(epoch_time)
    
    def perform_pii(self, line):
        """Perform pii in specified line."""
        for k, v in pii_list.items():
            extracted = v.findall(line)
            rep = "<{}>".format(k)
            for each in extracted:
                line = line.replace(each, rep)
        self.filtered_data += line
    
    def write_filtered(self):
        """Write back pii filtered content to file with original name."""
        filtered_file_path = os.path.join(self.filtered_dir, os.path.split(self.in_filename)[1])
        with open(filtered_file_path, 'w') as f:
            f.write(self.filtered_data)

#!/usr/bin/python3

import struct

class SauceParser():
    def __init__(self):
        # Open the file, look for a sauce record,
        # extract sauce data into a structure
        #self.fileName = filename

        # sauce data
        self.title = None
        self.author = None
        self.group = None
        self.date = None
        self.year = None
        self.month = None
        self.day = None
        self.fileType = None
        self.tinfo1 = None
        self.tinfo2 = None
        self.width = 80
        self.height = 25

        # sauce data offsets
        self.title_offset = 7
        self.author_offset = 42
        self.group_offset = 62
        self.date_offset = 82
        self.fileType_offset = 95
        self.tinfo1_offset = 96
        self.tinfo2_offset = 98
        # Number of lines in the extra SAUCE comment block. 1 byte.  0 indicates no comment block is present. 
        self.comnt_lines = 105
        self.comnt_first_line = 133 # comment lines are 64 bytes long

        # other stuff
        self.sauce_blob = None
        self.sauce_found = False


    def parse_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                file_blob = file.read()
        except Exception as E:
            return False
        self.parse_blob(file_blob)
        #return self.parse_blob(file_blob)  # Nothing to return..

    def parse_blob(self, file_blob):     # Blob is, like. Bytes or something
        sauce_blob = file_blob[-128:]
        self.sauce_blob = sauce_blob
        #print(sauce_blob)
        if sauce_blob[:5] == b"SAUCE":
            self.sauce_found = True
            self.title = struct.unpack_from('35s', sauce_blob, offset=self.title_offset)[0]
            self.author = struct.unpack_from('20s', sauce_blob, offset=self.author_offset)[0]
            self.group = struct.unpack_from('20s', sauce_blob, offset=self.group_offset)[0]
            self.date = struct.unpack_from('8s', sauce_blob, offset=self.date_offset)[0].decode()
            self.year = self.date[:4]
            self.month = self.date[4:][:2]
            self.day = self.date[4:][2:]

            # turn bytes into nicer strings
            try:
                self.title = self.title.decode().rstrip(' ').strip('\x00')
            except UnicodeDecodeError:
                self.title = self.title.decode('cp437').rstrip(' ').strip('\x00')
            try:
                self.author= self.author.decode().rstrip(' ').strip('\x00')
            except UnicodeDecodeError:
                self.author= self.author.decode('cp437').rstrip(' ').strip('\x00')
            try:
                self.group= self.group.decode().rstrip(' ').strip('\x00')
            except UnicodeDecodeError:
                self.group= self.group.decode('cp437').rstrip(' ').strip('\x00')
     
            self.tinfo1 = struct.unpack_from('H', sauce_blob, offset=self.tinfo1_offset)[0]
            if self.tinfo1 > 1:
                self.width = self.tinfo1

            self.tinfo2 = struct.unpack_from('H', sauce_blob, offset=self.tinfo2_offset)[0]
            if self.tinfo2 > 1:
                self.height = self.tinfo2
        else:
            self.sauce_found = False

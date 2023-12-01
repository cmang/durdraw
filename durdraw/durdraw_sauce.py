#!/usr/bin/python3

import struct

class EmptySauce():
    def __init__(self):
        self.fileName = None
        # sauce data
        self.title = None
        self.author = None
        self.group = None
        self.date = None
        self.fileType = None
        self.tinfo1 = None
        self.tinfo2 = None
        self.width = 80
        self.height = 25
        self.sauce_blob = None
        self.sauce_found = False


class SauceParser():
    def __init__(self, filename):
        # Open the file, look for a sauce record,
        # extract sauce data into a structure
        self.fileName = filename

        # sauce data
        self.title = None
        self.author = None
        self.group = None
        self.date = None
        self.fileType = None
        self.tinfo1 = None
        self.tinfo2 = None
        self.width = None
        self.height = None

        # stupid offsets
        self.title_offset = 7
        self.author_offset = 42
        self.group_offset = 62
        self.fileType_offset = 95
        self.tinfo1_offset = 96
        self.tinfo2_offset = 98

        # other stuff
        self.sauce_blob = None
        self.sauce_found = False

        self.load_and_parse_file(filename)

    def load_and_parse_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                file_blob = file.read()
        except Exception as E:
            return False

        sauce_blob = file_blob[-128:]
        self.sauce_blob = sauce_blob
        #print(sauce_blob)
        if sauce_blob[:5] == b"SAUCE":
            self.sauce_found = True
            self.title = struct.unpack_from('35s', sauce_blob, offset=self.title_offset)[0]
            self.author = struct.unpack_from('20s', sauce_blob, offset=self.author_offset)[0]
            self.group = struct.unpack_from('20s', sauce_blob, offset=self.group_offset)[0]

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
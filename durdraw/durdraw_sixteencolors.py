#!/usr/bin/python3 

import pdb

import json
import urllib.request

# exmaple data:
# [{'year': 1990, 'packs': 5}, {'year': 1991, 'packs': 7}]
# packs for 1992: ['1992', 'aaa-vol2', 'acdu0692', 'acdu0792', 'acdu0892', 'acdu0992', 'acdu1092', 'acdu1192', 'acdu1292', 'ace-r2', 'acid_a-d', 'acid_e-k', 'acid_l-r', 'acid_s-z', 'acidvga', 'air', 'allmack1', 'ansi', 'ansitoon', 'anssmp50', 'dead', 'grim-03', 'hipe', 'hype', 'icepk-08', 'icepk-09', 'icepk-10', 'icepk-11', 'icepk-12', 'image', 'jism', 'lgc-1292', 'ltd', 'mace', 'mirage', 'mirage01', 'mirage02', 'mirage03', 'mirage04', 'nc-17', 'paranoi2', 'paranoia', 'qck-pkt1', 'rpm', 'sda', 'z-md2']
# files for 1992/grim-03: {'name': 'grim-03', 'year': 1992, 'filename': 'grim-03.zip', 'month': '01', 'uri': '/pack/grim-03', 'groups': [], 'pack_file_location': '/archive/1992/grim-03.zip', 'files': [{'filename': 'CA-TUGO.ANS', 'file_location': '/ pack/grim-03/raw/CA-TUGO.ANS', 'uri': '/pack/grim-03/raw/CA-TUGO.ANS', 'fullsize': '/pack/grim-03/raw/CA-TUGO.ANS.png', 'th umbnail': '/pack/grim-03/tn/CA-TUGO.ANS.png', 'packs': {'filename': 'grim-03.zip', 'name': 'grim-03', 'uri': '/pack/grim-03 '}}, {'filename': 'CD-HOG1.EXE', 'file_location': '/pack/grim-03/raw/CD-HOG1.EXE'

class SixteenColorsAPI:
    def __init__(self):
        self.api_prefix="https://api.sixteencolors.net/v0"
        self.api_year_prefix="/year"
        self.api_suffix="?rows=0"
        self.year_listing_data = []     # cache for /year
        self.cache_years()
        self.url_cache = {}     # {"pack": {"filename": url, "filename2": url}}

        self.website_prefix="https://16colo.rs"

    def list_years(self):
        years_list = []
        for item in self.year_listing_data:
            years_list.append(str(item['year']))
        return years_list

    def cache_years(self):
        url = self.api_prefix + self.api_year_prefix + self.api_suffix
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                self.year_listing_data = json.loads(data)
        except urllib.request.HTTPError:
            return False
        return True

    def list_packs_for_year(self, year):
        url = self.api_prefix + self.api_year_prefix + '/' + str(year) + self.api_suffix
        #print(f"url: {url}")
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                packs_json_data = json.loads(data)  # list of dicts
        except urllib.request.HTTPError:
            return False
        file_list = []
        #print(f"{year} Packs JSON data: {packs_json_data}")
        for item in packs_json_data:
            #file_list.append(item['filename'])
            file_list.append(str(item['name']))
        return file_list

    def list_files_for_pack(self, pack):
        url = self.api_prefix + '/pack/' + str(pack) + self.api_suffix
        #print(f"list files for pack url: {url}")
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                pack_files_json_data = json.loads(data)  # list of dicts
        except urllib.request.HTTPError:
            return False
        file_list = []
        try:
            for item in pack_files_json_data['files']:
                file_list.append(item['filename'])
        except TypeError:   # got list instead of a dict?
            pdb.set_trace()
        return file_list

    def get_url_for_file(self, pack, filename):
        if pack in self.url_cache:
            if filename in self.url_cache[pack]:
                # cached, so return from cache
                return self.url_cache[pack][filename]

        # not cached
        url = self.api_prefix + '/pack/' + str(pack) + self.api_suffix
        #print(f"url: {url}")
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
                pack_files_json_data = json.loads(data)  # list of dicts
        except urllib.request.HTTPError:
            return False
        location = None
        for item in pack_files_json_data['files']:
            if item['filename'] == filename:
                #location = item['uri']
                location = item['file_location']
        #print(f"Get URL for File JSON data: {pack_files_json_data}")
        if location == None:
            url = ''
        else:
            url = self.website_prefix + urllib.parse.quote(location)
        if pack not in self.url_cache:
            self.url_cache[pack] = {}
        if filename not in self.url_cache[pack]:
            self.url_cache[pack][filename] = url
        return url

    def get_raw_file(self, pack, filename):
        url = self.get_url_for_file(pack, filename)
        #print(f"url: {url}")
        try:
            with urllib.request.urlopen(url) as response:
                data = response.read()
        except urllib.request.HTTPError:
            return False
        #return data.decode(encoding='cp437')
        return data

    #def diz_cache_for_year(year):
    #    """ returns a dict, like {"packname": dizdata} """

if __name__=="__main__":
    sixteen_web = SixteenColorsAPI()
    base_listing = sixteen_web.list_years()
    print(f"base listing: {base_listing}")
    year = 1992
    packs = sixteen_web.list_packs_for_year(year)
    print(f"packs for {year}: {packs}")
    pack = "grim-03"
    files = sixteen_web.list_files_for_pack(pack)
    print(f"files for {year}/{pack}: {files}")
    file = 'NE-EXEC.ANS'
    file_url = sixteen_web.get_url_for_file(pack, file)
    print(f"url for {year}/{pack}/{file}: {file_url}")
    #diz_cache = {}
    #diz_cache = diz_cache_for_year(year)    # dict
    #print(str(diz_cache))
    #ansi_data = sixteen_web.get_raw_file(pack, file)
    #print("Raw ansi data:")
    #print(ansi_data.decode(encoding='cp437'))




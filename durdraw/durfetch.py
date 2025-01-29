# Front-end to Durdraw and Neofetch

import argparse
import glob
import os
import pathlib
import random

from durdraw import log
import durdraw.main as durdraw_main
import durdraw.neofetcher as neofetcher
from durdraw.durdraw_version import DUR_VER

def all_durf_files():
    return all_internal_durf_files()

def all_internal_durf_files():
    # Return a list of all files from every location everywhere, throughout the universe
    # .. or at least the fetch animations built-in to durdraw (in the durdraw/durf/ path).
    internal_durf_path = pathlib.Path(__file__).parent.joinpath("durf/")
    internal_durf_files = glob.glob(f"{internal_durf_path}/*.durf")
    all_files = internal_durf_files
    #all_files = ['bsd.durf', 'linux-tux.durf', 'linux-fire.durf', 'unixbox.durf', 'cm-eye.durf']
    return all_files

def get_internal_durf_path():
    return str(pathlib.Path(__file__).parent.joinpath("durf/"))

def remove_suffix(text, suffix):
    # For compatibility with older Python versions, older than 3.8.
    # thanks, David Foster @ https://stackoverflow.com/questions/1038824/how-do-i-remove-a-substring-from-the-end-of-a-string-remove-a-suffix-of-the-str
    return text[:-len(suffix)] if text.endswith(suffix) and len(suffix) != 0 else text

def make_epilog():
    text = "Available animations for -l:\n\n"
    internal_file_list = []
    for filename in all_internal_durf_files():
        #basename = os.path.basename(filename)
        #print(basename)
        #name = os.path.basename(filename).removesuffix('.durf')
        name = remove_suffix(os.path.basename(filename), '.durf')
        internal_file_list.append(name)
    internal_file_list.sort()
    for name in internal_file_list:
        text += f"{name}\n"
    text += "\n"
    text += "\n"
    return text

def auto_load_file(neofetch_data, rand=False, fake_os=None):
    files = []
    if fake_os:
        os_name = fake_os
    else:
        os_name = neofetch_data['OS'].lower()
    if rand:
        files = all_durf_files()
        return random.choice(files)
    #if 'bsd' in neofetch_data['OS'].lower():
    bsd_list = ['bsd', 'macos']
    linux_list = ['linux']
    # Match BSD OSs
    if any(substring in os_name for substring in bsd_list):
        files = ['bsd.durf']
        # list of BSD 
    else:
        files = ['linux-fire.durf', 'linux-tux.durf']
    return random.choice(files)

@log.log_on_crash
def main():

    epilog_text = make_epilog()
    
    #print(epilog_text)

    parser = argparse.ArgumentParser(description="An animated fetcher. A front-end for Durdraw and Neofetch integration.", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog_text)
    parser.add_argument("filename", nargs='*', help=".durf ASCII and ANSI art file or files to use")
    #parser.add_argument("--list", help="List available Durfetch screens", action=store_true)
    parser_source_mutex = parser.add_mutually_exclusive_group()
    parser_source_mutex.add_argument("-r", "--rand", help="Pick a random animation to play", action="store_true")
    parser_source_mutex.add_argument("-l", "--load", help="Load an internal animation", nargs=1, type=str)
    parser_fake_os_mutex = parser.add_mutually_exclusive_group()
    parser_fake_os_mutex.add_argument("--linux", help="Show a Linux animation", action="store_true")
    parser_fake_os_mutex.add_argument("--bsd", help="Show a BSD animation", action="store_true")
    parser.add_argument("-V", "--version", help="Show Version information and quit", action="store_true")
    #parser.add_argument("-l", nargs="?", default="list")
    args = parser.parse_args()
    neofetch_data = neofetcher.run()
    #print(args.filename, args.list, args.l, neofetch_data)
    #if args.filename == None:   # no file name passed, so pick an appropriate one.
    faked = None
    if args.version:
        print(DUR_VER)
        exit(0)
    if args.linux:
        faked = "linux"
    if args.bsd:
        faked = "bsd"
    if args.load:
        filename = [get_internal_durf_path() + "/" + args.load[0] + ".durf"]
        if not os.path.isfile(filename[0]):
            print(f"Error: Could not find an animation by that name at {filename[0]}")
            exit(1)
    elif args.filename == []:   # no file name passed, so pick an appropriate one.
        if args.rand:   # don't prefix path, cuz all_dur_files() already did it
            filename = [auto_load_file(neofetch_data, rand=args.rand, fake_os=faked)]
        else:
            filename = [get_internal_durf_path() + "/" + auto_load_file(neofetch_data, fake_os=faked)]
    else:
        filename = args.filename
    #print(filename)

    durdraw_args = ["--fetch", "--play"] + filename # filename is alist
    durdraw_main.main(fetch_args=durdraw_args)

    

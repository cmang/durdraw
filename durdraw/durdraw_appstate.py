import gzip
import os
import pdb
import pickle
import subprocess
from durdraw.durdraw_options import Options
import durdraw.durdraw_file as durfile

class AppState():
    """ run-time app state, separate from movie options (Options()) """
    def __init__(self):
        self.curOpenFileName = ""
        self.playOnlyMode = False
        self.playNumberOfTimes = 0  # 0 = loop forever, default
        self.ansiLove = self.isAppAvail("ansilove")
        self.PIL = self.checkForPIL()
        self.undoHistorySize = 100  # How far back our undo history can
        self.playbackRange = (1,1)
        self.hasMouse = True # replace with equivalent curses.has_mouse()
        self.helpMov = None
        self.hasHelpFile = False
        self.playingHelpScreen = False
        self.durVer = None
        self.debug = False
        self.durFileVer = 0

    def setDurFileVer(self, durFileVer):  # file format for saving. 1-4 are pickle, 5+ is JSON
        self.durFileVer = durFileVer

    def setDurVer(self, version):
        self.durVer = version

    def setDebug(self, isEnabled: bool):
        self.debug = isEnabled

    def checkForPIL(self):
        try:
            import PIL
            return True
        except ImportError:
            return False

    def isAppAvail(self, name):   # looks for program 'name' in path
        try:
            devnull = open(os.devnull)
            subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
        except OSError as e:
            #if e.errno == os.errno.ENOENT:
            #    return False
            return False
        return True

    def loadHelpFile(self, helpFileName):
        helpFileName = os.path.expanduser(helpFileName)
        #self.helpMov = Movie(self.opts) # initialize a new movie to work with
        try:
            f = open(helpFileName, 'rb')
        except Exception as e:
            self.hasHelpFile = False
            self.helpMov = None
            return False
        if (f.read(2) == b'\x1f\x8b'): # gzip magic number
            # file == gzip compressed
            f.close()
            try:
                f = gzip.open(helpFileName, 'rb')
            except Exception as e:
                self.hasHelpFile = False
                self.helpMov = None
                return False
        else:
            f.seek(0)
        try:    # Load json help file
            #pdb.set_trace()
            loadedContainer = durfile.open_json_dur_file(f)
            self.helpMovOpts = loadedContainer['opts']
            self.helpMov = loadedContainer['mov']
            self.hasHelpFile = True
            return True
        except:
            pass    # loading json help file failed for some reason, so...
        try:                             # load dur help file
            #self.opts = pickle.load(f)
            #self.mov = pickle.load(f)
            self.helpMovOpts = pickle.load(f)
            self.helpMov = pickle.load(f)
            self.hasHelpFile = True
            return True
        except Exception as e:
            self.hasHelpFile = False
            self.helpMov = None
            return False


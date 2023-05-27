# Durdraw file operations - stuff related to open, save, etc

import gzip
import pdb
import pickle
import json

from durdraw.durdraw_options import Options
from durdraw.durdraw_movie import Movie


old_16_pal_to_new = {
    # maps old durdraw colors, found in file version 5 and lower
    # for 16 color
    0: 0,   # black
    1: 7,   # white/grey
    2: 3,   # cyan
    3: 5,   # magenta/purple
    4: 1,   # blue
    5: 6,   # brown/yellow
    6: 2,   # green
    7: 4,   # red
    8: 0,   # black
    9: 15,  # bright white
    10: 11, # bright cyan
    11: 13, # bright magenta
    12: 9,  # bright blue
    13: 14, # bright yellow
    14: 10, # bright green
    15: 12, # bright red
    16: 16, # bright black
}

old_256_pal_to_new = {
    # maps old durdraw colors, found in file version 5 and lower
    # for 16 color
    0: 0,   # black
    1: 7,   # white/grey
    2: 3,   # cyan
    3: 5,   # magenta/purple
    4: 1,   # blue
    5: 6,   # brown/yellow
    6: 2,   # green
    7: 4,   # red
    8: 241,   # bright black
    9: 8,  # bright red
    10: 9, # bright green
    11: 10, # bright yellow
    12: 11,  # bright blue
    13: 12, # bright magenta
    14: 13, # bright cyan
    15: 14, # bright white
    16: 15, # bright white
}


def serialize_to_json_file(opts, appState, movie, file_path, gzipped=True):
    """ Takes live Durdraw movie objects and serializes them out to a JSON files
    """
    colorMode = appState.colorMode
    if gzipped:
        opener = gzip.open
    else:
        opener = open
    with opener(file_path, 'wt') as f:
        movieDataHeader = {
            'formatVersion': opts.saveFileFormat,
            #'colorFormat': 'xterm-256', # ansi-16, xterm-256 
            'colorFormat': colorMode, # ansi-16, xterm-256 
            'preferredFont': 'fixed',   # fixed, vga, amiga, etc.
            #'encoding': 'Utf-8',
            'encoding': appState.charEncoding,
            'name': '',
            'artist': '',
            'framerate': opts.framerate,
            'sizeX': opts.sizeX,
            'sizeY': opts.sizeY,
            'extra': None,
            'frames': None,
            }
        frameNumber = 1
        fullMovie = {'DurMovie': movieDataHeader}
        fullMovieFrames = []
        for frame in movie.frames:
            content = ''
            newFrame = []
            newColorMap = []
            for posX in range(0, opts.sizeX):
                newColorMap.append(list())
                for posY in range(0, opts.sizeY):
                    #newColorMap[posX].append(list(frame.colorMap[posY, posX]))
                    newColorMap[posX].append(frame.newColorMap[posY][posX])
            for line in frame.content:
                content = ''.join(line)
                newFrame.append(content)
            serialized_frame = {
                'frameNumber': frameNumber,
                'delay': frame.delay,
                'contents': newFrame,
                'colorMap': newColorMap,
            }
            fullMovieFrames.append(serialized_frame)
            frameNumber += 1
        fullMovie['DurMovie']['frames'] = fullMovieFrames
        fullMovieJSON = json.dumps(fullMovie, indent=2)
        newMovieJSON = clean_up_json_output(fullMovieJSON)
        f.write(newMovieJSON)
    f.close()

def clean_up_json_output(json_str):
    """ Take aggressively whitespaced nested JSON lists and remove some of
    the excessive newlines and spaces. Basically format colorMap to
    look nicer
    """
    json_data = json_str
    json_data = json_data.replace("[\n            [", "[[")
    json_data = json_data.replace("[\n              ", "[")
    json_data = json_data.replace(",\n             ", ",")
    json_data = json_data.replace("\n            ],", "],")
    json_data = json_data.replace("],\n            [", "],[")
    json_data = json_data.replace("\n            ]", "]")
    json_data = json_data.replace("\n          ],", "],")
    return json_data

def get_dur_file_colorMode_and_charMode(f):
    """ Returns the color mode and encoding used by the file """
    f.seek(0)
    try:
        loadedMovieData = json.load(f)
    except Exception as E:
        return False
    colorMode = loadedMovieData['DurMovie']['colorFormat']
    try:
        charEncoding = loadedMovieData['DurMovie']['encoding']
    except Exception as E:
        charEncoding = 'utf-8'
    # convert from file format 5 to 6
    #if colorMode == 'xterm-256':
    #    colorMode = '256'
    if charEncoding == 'Utf-8':
        charEncoding = 'utf-8'
    return colorMode, charEncoding

def open_json_dur_file(f):
    """ Loads json file into opts and movie objects.  Takes an open file
    object. Returns the opts and mov objects, encased in a list object.
     Or return False if the open fails.
    """
    f.seek(0)
    try:
        loadedMovieData = json.load(f)
    except Exception as E:
        return False

    width = loadedMovieData['DurMovie']['sizeX']
    height = loadedMovieData['DurMovie']['sizeY']
    colorMode = loadedMovieData['DurMovie']['colorFormat']
    newOpts = Options(width=width, height=height)
    newOpts.framerate = loadedMovieData['DurMovie']['framerate']
    newOpts.saveFileFormat = loadedMovieData['DurMovie']['formatVersion']
    # load frames into a new movie object
    newMov = Movie(newOpts)
    currentFrame = 0
    lineNum = 0
    for frame in loadedMovieData['DurMovie']['frames']:
        newMov.insertCloneFrame()
        newMov.nextFrame()
        for line in frame['contents']:
            #pdb.set_trace()
            if lineNum < len(newMov.frames[currentFrame].content):
                newMov.frames[currentFrame].content[lineNum] = [c for c in line]
            #newMov.frames[currentFrame].content = line
            lineNum += 1
        lineNum = 0
        # load color map into new movie
        for x in range(0, width):
            for y in range(0, height):
                #pdb.set_trace()
                colorPair = frame['colorMap'][x][y]
                #if newOpts.saveFileFormat < 6:
                #    colorPair = convert_old_color_to_new(oldColorPair)
                #    if colorPair == None:
                #        pdb.set_trace()
                newMov.frames[currentFrame].colorMap[y, x] = tuple(colorPair)
                newMov.frames[currentFrame].newColorMap[y][x] = colorPair
        # Add delay for the frame
        newMov.frames[currentFrame].delay = frame['delay']
        currentFrame += 1
        #pdb.set_trace()
    newMov.deleteCurrentFrame()
    newMov.gotoFrame(1)
    container = {'opts':newOpts, 'mov':newMov}
    return container

def convert_old_color_to_new(oldPair, colorMode="16"):
    """ takes in a frame['colorMap'][x][y] list, returns a new list with
    [0] replaced by appropriately mapped # """
    #newPair = oldPair
    newFg = oldPair[0]
    newBg = oldPair[1]
    if colorMode == "16":
        if oldPair[0] in old_16_pal_to_new.keys():
            newFg = old_16_pal_to_new[oldPair[0]]
            newFg += 1
        if oldPair[1] in old_16_pal_to_new.keys():
            newBg = old_16_pal_to_new[oldPair[1]]
            #newBg += 1
    if colorMode == "256":
        if oldPair[0] in old_256_pal_to_new.keys():
            newFg = old_256_pal_to_new[oldPair[0]]
            newFg += 1
        #if oldPair[1] in old_16_pal_to_new.keys():
        #    newBg = old_16_pal_to_new[oldPair[1]]
        newBg = oldPair[1]    # 256 does not use bg color, so don't change it
    #pdb.set_trace()
    return [newFg, newBg]

def load_ascii_file(file):
    width = 0   # will increase as we load the file
    height = 0  # dito
    newOpts = Options(width=width, height=height)
    newOpts.framerate = loadedMovieData['DurMovie']['framerate']
    newOpts.saveFileFormat = loadedMovieData['DurMovie']['formatVersion']
    # load frames into a new movie object
    newMov = Movie(newOpts)
    currentFrame = 0
    lineNum = 0
    try:
        if self.appState.debug: self.notify("Trying to open() file as ascii.")
        f = open(filename, 'r')
        self.appState.curOpenFileName = os.path.basename(filename)
    except Exception as e:
        #if self.appState.debug: self.notify(f"self.opts = pickle.load(f)")
        self.notify(f"Could not open file for reading: {e}")
        return None
    # here we add the stuff to load the file into self.mov.currentFrame.content[][]
    self.undo.push()
    self.mov.currentFrame.initColorMap()
    linecount = 0
    for line in f:
        if (linecount < self.mov.sizeY):    # don't exceed canvas size
            inBuffer = list(line.strip('\n').ljust(self.mov.sizeX)) # Returns line as 80 column list of chars
            self.mov.currentFrame.content[linecount] = inBuffer
        linecount += 1
    f.close()
    for x in range(linecount, self.mov.sizeY):   # clear out rest of contents.
         self.mov.currentFrame.content[x] = list(" " * self.mov.sizeX)

class DurUnpickler(pickle.Unpickler):
    """" Custom Unpickler to remove serialized module names (like __main__) from
    unpickled data and replace them with "durdraw.durdraw_movie"
    """
    def find_class(self, module, name):
        #if module == "__main__":
        module = "durdraw.durdraw_movie"
        return super().find_class(module, name)


 

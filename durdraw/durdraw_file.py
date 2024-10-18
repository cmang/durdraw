# Durdraw file operations - stuff related to open, save, etc

import datetime
import gzip
import os
import pdb
import pickle
import json

from durdraw.durdraw_options import Options
from durdraw.durdraw_movie import Movie
# import durdraw.durdraw_ansiparse as ansiparse

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

colors_to_html = {
    # Maps Durdraw color numbers to HTML values
    0: '#000000',   # black
    1: '#000000',   # black
    2: '#0000AA',   # blue
    3: '#00AA00',   # green
    4: '#00AAAA',   # cyan
    5: '#AA0000',   # red
    6: '#AA00AA',   # magenta
    7: '#AA5500',   # brown/dark yellow
    8: '#AAAAAA',   # light gray/white
    9: '#555555',   # dark grey
    10: '#5555FF',   # bright blue
    11: '#55FF55',   # bright green
    12: '#55FFFF',  # bright cyan
    13: '#FF5555',  # bright red
    14: '#FF55FF',  # bright magenta
    15: '#FFFF00',  # bright yellow
    16: '#FFFFFF',  # bright white
}

def write_frame_to_html_file(mov, appState, frame, file_path, gzipped=False):
    """ Writes a single frame to an HTML file
    """
    colorMode = appState.colorMode
    if gzipped:
        opener = gzip.open
    else:
        opener = open
    with opener(file_path, 'wt') as f:
        movieDataHeader = '<!DOCTYPE html>\n'
        movieDataHeader += '<html lang="en">\n'
        movieDataHeader += ''
        movieDataHeader += '    <head>\n'
        movieDataHeader += '        <meta charset="utf-8">\n'
        movieDataHeader += '        <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        movieDataHeader += '        <title>DurDraw Generated Output</title>\n'
        movieDataHeader += '        <style>\n'
        movieDataHeader += '            body {\n'
        movieDataHeader += '                color: #FFFFFF;\n'
        movieDataHeader += '                background-color: #000000;\n'
        movieDataHeader += '            }\n'
        movieDataHeader += '            #duroutput {\n'
        movieDataHeader += '                font-size:12pt;\n'
        movieDataHeader += '                font-family: "Courier New", monospace;\n'
        # movieDataHeader += '              font-family: monospace,monospace;\n'
        movieDataHeader += '                line-height:13pt;\n'
        movieDataHeader += '                color: #FFFFFF;\n'
        movieDataHeader += '            }\n'
        movieDataHeader += '        </style>\n'
        movieDataHeader += '    </head>\n'
        movieDataHeader += '    <body>\n'
        movieDataHeader += '        <pre id="duroutput">\n'

        fileContent = movieDataHeader
        #lineNum = 0
        #colNum = 0
        newColorMap = []
        for posY in range(0, mov.sizeY):
            #newColorMap.append(list())
            for posX in range(0, mov.sizeX):
                #newColorMap[posX].append(list(frame.colorMap[posY, posX]))
                #newColorMap[posX].append(frame.newColorMap[posY][posX])
                durDolor = frame.newColorMap[posY][posX]
                fgColor = frame.newColorMap[posY][posX][0]
                bgColor = frame.newColorMap[posY][posX][1]
                c = frame.content[posY][posX]
        #for line in frame.content:
        #    for c in line: 
                try:
                    #fgColor = frame.newColorMap[colNum][lineNum][0]
                    #bgColor = frame.newColorMap[colNum][lineNum][1]
                    if appState.colorMode == "16":
                        bgColor += 1
                        if bgColor == 9:    # black duplicate
                            bgColor = 0
                    if appState.colorMode == "256":
                        fgColor += 1
                        bgColor += 1
                    if fgColor in colors_to_html.keys():
                        fgHtmlColor = colors_to_html[fgColor]
                    else:
                        fgHtmlColor = '#AAAAAA'
                    if bgColor in colors_to_html.keys():
                        bgHtmlColor = colors_to_html[bgColor]
                    else:
                        bgHtmlColor = '#000000'
                    #fileContent += f"<div style=\"color: {fgHtmlColor}; background-color: {bgHtmlColor}; display: inline;\">"
                    fileContent += f"<span style=\"color: {fgHtmlColor}; background-color: {bgHtmlColor};\">"
                    #fileContent += f"<font color={fgHtmlColor} style=\"background-color: {bgHtmlColor};\">"
                    #fileContent += f"<font color={fgHtmlColor} background-color={bgHtmlColor}>"
                    fileContent += str(c)
                    fileContent += "</span>"
                    #fileContent += "</div>"
                    #colNum += 1
                except Exception as e:
                    print(str(e))
                    pdb.set_trace()
            fileContent += '\n'
            #lineNum += 1
        
        fileContent += '        </pre>\n'
        fileContent += '    </body>\n'
        fileContent += '</html>\n'
        f.write(fileContent)
    f.close()

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
            'colorFormat': colorMode, # 16, 256
            'preferredFont': 'fixed',   # fixed, vga, amiga, etc.
            'encoding': appState.charEncoding,
            'name': '',
            'artist': '',
            'framerate': opts.framerate,
            'sizeX': movie.sizeX,
            'sizeY': movie.sizeY,
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
            for posX in range(0, movie.sizeX):
                newColorMap.append(list())
                for posY in range(0, movie.sizeY):
                    #newColorMap[posX].append(list(frame.colorMap[posY, posX]))
                    try:
                        newColorMap[posX].append(frame.newColorMap[posY][posX])
                    except Exception as E:
                        print(E)
                        pdb.set_trace()
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

def get_file_mod_date_time(filename):
    """ Returns a string like this: 2009-10-06 10:50:01 """
    t = os.path.getmtime(filename)
    return str(datetime.datetime.fromtimestamp(t, tz=datetime.timezone.utc))[:19]


def get_dur_file_colorMode_and_charMode(f):
    """ Returns the color mode and encoding used by the file """
    f.seek(0)
    try:
        loadedMovieData = json.load(f)
    except Exception as e:
        return False
    colorMode = loadedMovieData['DurMovie']['colorFormat']
    try:
        charEncoding = loadedMovieData['DurMovie']['encoding']
    except Exception as e:
        charEncoding = 'utf-8'
    # convert from file format 5 to 6
    #if colorMode == 'xterm-256':
    #    colorMode = '256'
    if charEncoding == 'Utf-8':
        charEncoding = 'utf-8'
    return colorMode, charEncoding

def open_json_dur_file(f, appState):
    """ Loads json file into opts and movie objects.  Takes an open file
    object. Returns the opts and mov objects, encased in a list object.
     Or return False if the open fails.
    """
    f.seek(0)
    try:
        loadedMovieData = json.load(f)
    except Exception as e:
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
        #newMov.insertCloneFrame()
        newMov.addEmptyFrame()
        newMov.nextFrame()
        for line in frame['contents']:
            #pdb.set_trace()
            if lineNum < len(newMov.frames[currentFrame].content):
                newMov.frames[currentFrame].content[lineNum] = [c for c in line]
                #newMov.frames[currentFrame].content[lineNum] = [c for c in line.encode(appState.charEncoding)]
                #newMov.frames[currentFrame].content[lineNum] = [c for c in bytes(line).decode('cp437')]
            #newMov.frames[currentFrame].content = line
            lineNum += 1
        lineNum = 0
        # load color map into new movie
        #pdb.set_trace()
        for x in range(0, width):
            for y in range(0, height):
                #pdb.set_trace()
                colorPair = frame['colorMap'][x][y]
                if appState.colorMode == '16' and colorMode == '256':
                    # set a default color when down-converting color modes:
                    if colorPair[0] > 16:
                        colorPair = [8,0]
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


class DurUnpickler(pickle.Unpickler):
    """" Custom Unpickler to remove serialized module names (like __main__) from
    unpickled data and replace them with "durdraw.durdraw_movie"
    """
    def find_class(self, module, name):
        #if module == "__main__":
        module = "durdraw.durdraw_movie"
        return super().find_class(module, name)


 

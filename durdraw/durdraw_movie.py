from copy import deepcopy
from durdraw.durdraw_options import Options
import durdraw.log as log
import json
import pdb
import re

import curses

def init_list_colorMap(width, height):
    """ Builds a color map consisting of a list of lists """
    #return [[list([1,0]) * width] * height]
    colorMap = []
    for h in range(0, height):
        colorMap.append([])
        for w in range(0, width):
            colorMap[h].append([8, 0])
    return colorMap

def convert_dict_colorMap(oldMap, width, height):
    """ Converts the old {[x,y] = (1,0)} color map
    into new format: [x, y] = [1, 0] """
    newMap = init_list_colorMap(width, height)
    for x in range(0, height):
        for y in range(0, width):
            newMap[x][y] = list(oldMap[(x, y)])   # wtf was I thinking
    #print(f"New color map: {newMap}")   # DEBUG
    return newMap

def convert_movie_16_to_256_color_palette(mov):
    """ Takes movie with old 16 color palette, converts it to look
    correct with 256 color palette. Returns converted movie? """
    fixer = {   # conversion table for the palettes
            # old and bad:
            # dim: 1 = white, 2 = cyan, 3 = purple, 4 = blue, 5 = brown, 6 = green, 7 = red, 8 = black
            # bright: 9 = white, 10 = cyan, 11 = purple, 12 = blue, 13 = brown, 14 = green, 15 = red, 16 = bright grey 
            # new and good:
            # 
            9: 15,  # bright white
            10: 14, # bright cyan
            11: 13, # bright purple
            12: 12, # bright blue, 
            13: 11, # bright yellow
            14: 10, # bright green
            15: 9, # bright red
            16: 242 # bright gray
        }
    for frame in mov.frames:
        # apply the fixer{} mapping to the frame's color map
        # looks something like: frame.colorMap[posY, posX]
        # returns a tuple, not a list. yeegh
        pass
        #for line in frame:

class Frame():
    """Frame class - single canvas size frame of animation. a traditional drawing.
    """
    def __init__(self, columns, lines):
        """ Initialize frame, content[x][y] grid """
        # it's a bunch of rows of ' 'characters.
        self.content = []
        #self.colorMap = {}
        #pdb.set_trace()
        self.sizeX = columns
        self.sizeY = lines 
        if isinstance(self.sizeY, int):
            self.newColorMap = init_list_colorMap(self.sizeX, self.sizeY)   # [[1,0], [3, 1], ...]
        else:
            curses.def_prog_mode() 
            curses.endwin()
            pdb.set_trace()
            curses.reset_prog_mode() 
        self.delay = 0  # delay == # of sec to wait at this frame.

        # Generate character arrays for frame contents, fill it
        # with ' ' (space) characters
        for x in range(0, lines):
            self.content.append([])
            for y in range(0, columns):
                self.content[x].append(' ')

        #self.initOldColorMap()
        #self.initColorMap()
        #self.newColorMap = convert_dict_colorMap(self.colorMap, width, height)
        self.setDelayValue(0)

        self.log = log.getLogger('frame')
        self.log.info('frame initialized', {'width': columns, 'height': lines})

    @property
    def colorMap(self):
        return self.newColorMap

    @colorMap.setter
    def colorMap(self, value):
        self.newColorMap = value

    def flip_horizontal(self):
        #pdb.set_trace()
        self.content = self.content[::-1]
        self.newColorMap.reverse()
        #for x in range(0, self.height):
        #    #for y in range(0, self.width):
        #    # reverse slicing trick
        #    self.content[x] = self.content[x][::-1]
        #    #self.content[x][0] = self.content[x][0][::-1]
        #    self.newColorMap[x].reverse()

    def flip_vertical(self):
        for x in range(0, self.height):
            #for y in range(0, self.width):
            # reverse slicing trick
            self.content[x] = self.content[x][::-1]
            #self.content[x][0] = self.content[x][0][::-1]
            self.newColorMap[x].reverse()

    #def flip_horizontal_segment(self, startPoint, height, width, frange=None):
    #    """ Finish writing this, use it for the alt-k select """
    #    for x in range(0, self.height):
    #        self.content[x].reverse()
    #        self.newColorMap[x].reverse()

    def width(self):
        """ Returns the number of columns in the frame """
        return self.sizeX

    def height(self):
        """ Returns the number of lines in the frame """
        return self.sizeY

    def setWidth(self, columns):
        self.sizeX = columns 
        return true

    def setHeight(self, lines):
        self.sizeY = lines 
        return true


    def setDelayValue(self, delayValue):
        self.delay = delayValue

    def initColorMap(self, fg=7, bg=0):
        """ Builds a list of lists """
        return [[[fg,0] * self.sizeY] * self.sizeX]

class Movie():
    """ Contains an array of Frames, options to add, remove, copy them """
    def __init__(self, opts):
        self.frameCount = 0  # total number of frames
        self.currentFrameNumber = 0
        self.sizeX = opts.sizeX     # Number of columns
        self.sizeY = opts.sizeY     # Number of lines
        self.opts = opts
        self.frames = []
        self.layers = {}    # Key can be a layer #, or something special. eg: "masks
        self.addEmptyFrame()
        self.currentFrameNumber = self.frameCount
        self.currentFrame = self.frames[self.currentFrameNumber - 1]

        self.log = log.getLogger('movie')
        self.log.info('movie initialized', {'sizeX': self.sizeX, 'sizeY': self.sizeY})

    def width(self):
        """ Returns the number of columns in the movie """
        return self.sizeX

    def height(self):
        """ Returns the number of lines in the movie """
        return self.sizeY

    def addFrame(self, frame):
        """ takes a Frame object, adds it into the movie """
        self.frames.append(frame)
        self.frameCount += 1
        return True

    def insertFrame(self, frame):
        """ takes a Frame object, inserts it after current frame """
        self.frames.insert(self.currentFrameNumber, frame)
        self.frameCount += 1
        return True

    def addEmptyFrame(self):
        newFrame = Frame(self.sizeX, self.sizeY)
        self.frames.append(newFrame)
        self.frameCount += 1
        return True

    def insertCloneFrame(self):
        """ clone current frame after current frame """
        newFrame = Frame(self.sizeX, self.sizeY)
        self.frames.insert(self.currentFrameNumber, newFrame)
        newFrame.content = deepcopy(self.currentFrame.content)
        #newFrame.colorMap = deepcopy(self.currentFrame.colorMap)
        newFrame.newColorMap = deepcopy(self.currentFrame.newColorMap)
        self.frameCount += 1
        return True

    def deleteCurrentFrame(self):
        if (self.frameCount == 1):
            del self.frames[self.currentFrameNumber - 1]
            # deleted the last frame, so make a blank one
            newFrame = Frame(self.sizeX, self.sizeY)
            self.frames.append(newFrame)
            self.currentFrame = self.frames[self.currentFrameNumber - 1]
        else:
            del self.frames[self.currentFrameNumber - 1]
            self.frameCount -= 1
            if (self.currentFrameNumber != 1):
                self.currentFrameNumber -= 1
            self.currentFrame = self.frames[self.currentFrameNumber - 1]
        return True

    def moveFramePosition(self, startPosition, newPosition):
        """ move the frame at startPosition to newPosition """
        # use push and pop to remove and insert it
        fromIndex = startPosition - 1
        toIndex = newPosition - 1
        self.frames.insert(toIndex, self.frames.pop(fromIndex))

    def gotoFrame(self, frameNumber):
        if frameNumber > 0 and frameNumber < self.frameCount + 1:
            self.currentFrameNumber = frameNumber
            self.currentFrame = self.frames[self.currentFrameNumber - 1]
            return True # succeeded
        else:
            return False # failed - invalid input

    def nextFrame(self):
        if (self.currentFrameNumber == self.frameCount):    # if at last frame..
            self.currentFrameNumber = 1     # cycle back to the beginning
            self.currentFrame = self.frames[self.currentFrameNumber - 1] # -1 bcuz frame 1 = self.frames[0]
        else:
            self.currentFrameNumber += 1
            self.currentFrame = self.frames[self.currentFrameNumber - 1]

    def prevFrame(self):
        if (self.currentFrameNumber == 1):
            self.currentFrameNumber = self.frameCount
            self.currentFrame = self.frames[self.currentFrameNumber - 1]
        else:
            self.currentFrameNumber -= 1
            self.currentFrame = self.frames[self.currentFrameNumber - 1]

    def hasMultipleFrames(self):
        if len(self.frames) > 1:
            return True
        else:
            return False

    def growCanvasWidth(self, growth):
        self.sizeX += growth
        self.opts.sizeX += growth

    def shrinkCanvasWidth(self, shrinkage):
        self.sizeY = self.sizeY - shrinkage
        self.opts.sizeY = self.opts.sizeY - shrinkage 

    def search_and_replace_color_pair(self, old_color, new_color, frange=None):
        if frange != None:  # apply to all frames in range
            for frameNum in range(frange[0] - 1, frange[1]):
            #for frame in self.frames:
                frame = self.frames[frameNum]
                line_num = 0
                col_num = 0
                for line in frame.newColorMap:
                    for pair in line:
                        if pair == old_color:
                            try:
                                frame.newColorMap[line_num][col_num] = new_color
                            except:
                                pdb.set_trace()
                            #found = True
                        col_num += 1
                    line_num += 1
                    col_num = 0
        else:   # only apply to current frame
            frame = self.currentFrame
            line_num = 0
            col_num = 0
            for line in frame.newColorMap:
                for pair in line:
                    if pair == old_color:
                        try:
                            frame.newColorMap[line_num][col_num] = new_color
                        except:
                            pdb.set_trace()
                        #found = True
                    col_num += 1
                line_num += 1
                col_num = 0


    def search_and_replace_color(self, old_color :int, new_color :int):
        found = False
        for frame in self.frames:
            line_num = 0
            for line in frame.newColorMap:
                for pair in line:
                    if pair[0] == old_color:
                        frame.newColorMap[line_num][0] = new_color
                        found = True
                    if pair[1] == old_color:
                        frame.newColorMap[line_num][1] = new_color
                        found = True
                line_num += 1

    def search_and_replace_char(self, old_char: str, new_char: str, frange = None):
        for frame in self.frames:
            line_num = 0
            while line_num < frame.sizeY:
                col_num  = 0
                #for col in line:
                while col_num < frame.sizeX:
                    if frame.content[line_num][col_num] == old_char:
                        frame.content[line_num][col_num] = new_char
                    col_num += 1
                line_num += 1

        if frange != None:  # apply to all frames in range
            for frameNum in range(frange[0] - 1, frange[1]):
            #for frame in self.frames:
                frame = self.frames[frameNum]
                line_num = 0
                col_num = 0
                while line_num < frame.sizeY:
                    while col_num < frame.sizeX:
                        if frame.content[line_num][col_num] == old_char:
                            frame.content[line_num][col_num] = new_char
                        col_num += 1
                    line_num += 1
                    col_num = 0
        else:   # only apply to current frame
            frame = self.currentFrame
            line_num = 0
            col_num = 0
            while line_num < frame.sizeY:
                while col_num < frame.sizeX:
                    if frame.content[line_num][col_num] == old_char:
                        frame.content[line_num][col_num] = new_char
                    col_num += 1
                line_num += 1
                col_num = 0


    def search_and_replace(self, caller, search_str: str, replace_str: str):
        #search_list = list(search)
        found = False

        frame_num = 0
        line_num = 0
        for frame in self.frames:
            line_num = 0
            for line in frame.content:
                line_str = ''.join(line)
                if search_str in line_str:
                    # do regexp way, to keep justification
                    match = re.search(f"{search_str}\\s*", line_str)
                    if match:
                        # Calculate the exact width to replace
                        width = match.end() - match.start()
                        # Trim or pad replace_str to fit in the calculated width
                        replace_with = replace_str[:width].ljust(width)
                        # Substitute in the line
                        line_str = line_str[:match.start()] + replace_with + line_str[match.end():]

                    else:
                        # if that fails, do old way
                        if len(search_str) < len(replace_str):
                            #line_str = line_str.replace(search_str.ljust(len(replace_str)), replace_str)
                            line_str = line_str.replace(search_str, replace_str)
                        else:
                            line_str = line_str.replace(search_str, replace_str.ljust(len(search_str)))
                    # inject modified line back into frame
                    line = list(line_str)
                    frame.content[line_num] = line
                    found = True
                line_num += 1
            frame_num += 1
        return found


    def search_for_string(self, search_str: str, caller=None):
        #search_list = list(search)
        found = False
        frame_num = 0
        line_num = 0
        for frame in self.frames:
            line_num = 0
            for line in frame.content:
                line_str = ''.join(line)
                if search_str in line_str:
                    column_num = line_str.index(search_str) + 1
                    frame_num += 1
                    found = True
                    return {"line": line_num, "col": column_num, "frame": frame_num}
                line_num += 1
            frame_num += 1
        return found    # should be false if execution reaches this point


    def change_palette_16_to_256(self, frame=None):
        # Convert from blue to bright white by reducing their value by 1
        if frame:   # run it on just a frame.
            line_num = 0
            col_num = 0
            for line in frame.newColorMap:
                for pair in line:
                    if pair[0] == 1:    # black
                        frame.newColorMap[line_num][col_num][0] = 16
                    elif pair[0] == 16:    # bright white
                        frame.newColorMap[line_num][col_num][0] = 15
                    elif pair[0] == 15:    # bright yellow
                        frame.newColorMap[line_num][col_num][0] = 14
                    elif pair[0] == 14:    # bright purple
                        frame.newColorMap[line_num][col_num][0] = 13
                    elif pair[0] == 13:    # bright red
                        frame.newColorMap[line_num][col_num][0] = 12
                    elif pair[0] == 12:    # bright cyan
                        frame.newColorMap[line_num][col_num][0] = 11
                    elif pair[0] == 11:    # bright green
                        frame.newColorMap[line_num][col_num][0] = 10
                    elif pair[0] == 10:    # bright blue
                        frame.newColorMap[line_num][col_num][0] = 9
                    elif pair[0] == 9:    # bright black
                        frame.newColorMap[line_num][col_num][0] = 8
                    elif pair[0] == 8:    # grey
                        frame.newColorMap[line_num][col_num][0] = 7
                    elif pair[0] == 7:    # brown
                        frame.newColorMap[line_num][col_num][0] = 6
                    elif pair[0] == 6:    # purple
                        frame.newColorMap[line_num][col_num][0] = 5
                    elif pair[0] == 5:    # red
                        frame.newColorMap[line_num][col_num][0] = 4
                    elif pair[0] == 4:    # cyan
                        frame.newColorMap[line_num][col_num][0] = 3
                    elif pair[0] == 3:    # green
                        frame.newColorMap[line_num][col_num][0] = 2
                    elif pair[0] == 2:    # blue
                        frame.newColorMap[line_num][col_num][0] = 1
                    # eliminate all BG colors for now. 0 = black in 256 color mode.
                    # bg 8 = black in 16 color mode. We do this because things get
                    # weird in 256 color mode with non-0 BG colors.
                    pair[1] = 0         
                    col_num += 1
        else:   # run it on whole movie
            for frame in self.frames:
                line_num = 0
                col_num = 0
                for line in frame.newColorMap:
                    for pair in line:
                        if pair[0] == 1:    # black
                            pair[0] = 16
                        elif pair[0] == 16:    # bright white
                            pair[0] = 15
                        elif pair[0] == 15:    # bright yellow
                            pair[0] = 14
                        elif pair[0] == 14:    # bright purple
                            pair[0] = 13
                        elif pair[0] == 13:    # bright red
                            pair[0] = 12
                        elif pair[0] == 12:    # bright cyan
                            pair[0] = 11
                        elif pair[0] == 11:    # bright green
                            pair[0] = 10
                        elif pair[0] == 10:    # bright blue
                            pair[0] = 9
                        elif pair[0] == 9:    # bright black
                            pair[0] = 8
                        elif pair[0] == 8:    # grey
                            pair[0] = 7
                        elif pair[0] == 7:    # brown
                            pair[0] = 6
                        elif pair[0] == 6:    # purple
                            pair[0] = 5
                        elif pair[0] == 5:    # red
                            pair[0] = 4
                        elif pair[0] == 4:    # cyan
                            pair[0] = 3
                        elif pair[0] == 3:    # green
                            pair[0] = 2
                        elif pair[0] == 2:    # blue
                            pair[0] = 1
                        # eliminate all BG colors for now. 0 = black in 256 color mode.
                        # bg 8 = black in 16 color mode. We do this because things get
                        # weird in 256 color mode with non-0 BG colors.
                        pair[1] = 0         
                        col_num += 1

    def change_palette_256_to_16(self, frame=None):
        if frame:
            line_num = 0
            col_num = 0
            for line in frame.newColorMap:
                for pair in line:
                    if pair[0] == 16:    # black
                        pair[0] = 1
                    elif pair[0] == 15:    # bright white
                        pair[0] = 16
                    elif pair[0] == 14:    # bright yellow
                        pair[0] = 15
                    elif pair[0] == 13:    # bright purple
                        pair[0] = 14
                    elif pair[0] == 12:    # bright red
                        pair[0] = 13
                    elif pair[0] == 11:    # bright cyan
                        pair[0] = 12
                    elif pair[0] == 10:    # bright green
                        pair[0] = 11
                    elif pair[0] == 9:    # bright blue
                        pair[0] = 10
                    elif pair[0] == 8:    # bright black
                        pair[0] = 9
                    elif pair[0] == 7:    # grey
                        pair[0] = 8
                    elif pair[0] == 6:    # brown
                        pair[0] = 7
                    elif pair[0] == 5:    # purple
                        pair[0] = 6
                    elif pair[0] == 4:    # red
                        pair[0] = 5
                    elif pair[0] == 3:    # cyan
                        pair[0] = 4
                    elif pair[0] == 2:    # green
                        pair[0] = 3
                    elif pair[0] == 1:    # blue
                        pair[0] = 2
                    col_num += 1
        else:
            # Convert from blue to bright white by reducing their value by 1
            for frame in self.frames:
                line_num = 0
                col_num = 0
                for line in frame.newColorMap:
                    for pair in line:
                        if pair[0] == 16:    # black
                            pair[0] = 1
                        elif pair[0] == 15:    # bright white
                            pair[0] = 16
                        elif pair[0] == 14:    # bright yellow
                            pair[0] = 15
                        elif pair[0] == 13:    # bright purple
                            pair[0] = 14
                        elif pair[0] == 12:    # bright red
                            pair[0] = 13
                        elif pair[0] == 11:    # bright cyan
                            pair[0] = 12
                        elif pair[0] == 10:    # bright green
                            pair[0] = 11
                        elif pair[0] == 9:    # bright blue
                            pair[0] = 10
                        elif pair[0] == 8:    # bright black
                            pair[0] = 9
                        elif pair[0] == 7:    # grey
                            pair[0] = 8
                        elif pair[0] == 6:    # brown
                            pair[0] = 7
                        elif pair[0] == 5:    # purple
                            pair[0] = 6
                        elif pair[0] == 4:    # red
                            pair[0] = 5
                        elif pair[0] == 3:    # cyan
                            pair[0] = 4
                        elif pair[0] == 2:    # green
                            pair[0] = 3
                        elif pair[0] == 1:    # blue
                            pair[0] = 2
                        col_num += 1


    def contains_high_colors(self):
        """ Returns True if any color above 16 is used, False otherwise """
        for frame in self.frames:
            for line in frame.newColorMap:
                for pair in line:
                    if pair[0] > 16:
                        return True
        return False

    def contains_background_colors(self):
        """ Return true if any background color is set other than black or default """
        for frame in self.frames:
            for line in frame.newColorMap:
                for pair in line:
                    if pair[1] > 0:
                        return True
        return False

    def strip_backgrounds(self):
        """ Change all background colors to 0, or default background """
        for frame in self.frames:
            for line in frame.newColorMap:
                for pair in line:
                    pair[1] = 0
        return True

    def strip_unprintable_characters(self):
        """ Remove all non-printable characters from canvas """
        #frame_num = 0
        for frame in self.frames:
            line_num = 0
            col_num = 0
            for line in frame.content:
                for char in line:
                    if char.isprintable():
                        pass
                    else:   # Not a printable character, so replace it with a ' '
                        #line_str = line_str.replace(search_str, replace_str.ljust(len(search_str)))
                        #line = list(line_str)
                        frame.content[line_num][col_num] = ' '
                    col_num += 1
                col_num = 0
                line_num += 1
        return True

    def shift_right(self):
        """ Shift all frames to the right, wrapping the last frame back to the front """
        # a.insert(0,a.pop())
        self.frames.insert(0, self.frames.pop())
        return True

    def shift_left(self):
        """ Shift all frames to the left, wrapping the first frame around to the back end """
        # fnord.append(fnord.pop(0))
        self.frames.append(self.frames.pop(0))
        return True

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)



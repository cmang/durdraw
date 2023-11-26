from copy import deepcopy
from durdraw.durdraw_options import Options
import json

def init_list_colorMap(width, height):
    """ Builds a color map consisting of a list of lists """
    #return [[list([1,0]) * width] * height]
    colorMap = []
    dummyColor = [1, 0]
    for h in range(0, height):
        colorMap.append([])
        for w in range(0, width):
            colorMap[h].append(dummyColor)
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
    def __init__(self, width, height):
        """ Initialize frame, content[x][y] grid """
        # it's a bunch of rows of ' 'characters.
        self.content = []
        self.colorMap = {}
        self.newColorMap = init_list_colorMap(width, height)   # [[1,0], [3, 1], ...]
        self.sizeX = width
        self.width = width
        self.sizeY = height
        self.height = height
        self.delay = 0  # delay == # of sec to wait at this frame.
        for x in range(0, height):
            self.content.append([])
            for y in range(0, width):
                self.content[x].append(' ')
        self.initOldColorMap()
        #self.initColorMap()
        #self.newColorMap = convert_dict_colorMap(self.colorMap, width, height)
        self.setDelayValue(0)

    def setWidth(self, width):
        self.sizeX = width
        self.width = width
        return true

    def setHeight(self, height):
        self.sizeY = height
        self.height = height
        return true


    def setDelayValue(self, delayValue):
        self.delay = delayValue

    def initOldColorMap(self):
        """ Builds a dictionary mapping X/Y to a FG/BG color pair """
        self.colorMap = {}
        for x in range(0, self.sizeY):
            for y in range(0, self.sizeX):
                self.colorMap.update( {(x,y):(1,0)} )  # tuple keypair (xy), tuple value (fg and bg)

    def initColorMap(self, fg=7, bg=0):
        """ Builds a list of lists """
        return [[[fg,0] * self.sizeY] * self.sizeX]

class Movie():
    """ Contains an array of Frames, options to add, remove, copy them """
    def __init__(self, opts):
        self.frameCount = 0  # total number of frames
        self.currentFrameNumber = 0
        self.sizeX = opts.sizeX
        self.sizeY = opts.sizeY
        self.opts = opts
        self.frames = []
        self.addEmptyFrame()
        self.currentFrameNumber = self.frameCount
        self.currentFrame = self.frames[self.currentFrameNumber - 1]

    def addFrame(self, frame):
        """ takes a Frame object, adds it into the movie """
        self.frames.append(frame)
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
        newFrame.colorMap = deepcopy(self.currentFrame.colorMap)
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

    def growCanvasWidth(self, growth):
        self.sizeX += growth
        self.opts.sizeX += growth
        #self.width += growth

    def shrinkCanvasWidth(self, shrinkage):
        self.sizeY = self.sizeY - shrinkage
        self.opts.sizeY = self.opts.sizeY - shrinkage 
        #self.width = self.width - shrinkage

    def contains_high_colors(self):
        """ Returns True if any color above 16 is used, False otherwise """
        for frame in self.frames:
            for line in frame.newColorMap:
                for pair in line:
                    if pair[0] > 16:
                        return True
        return False

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)



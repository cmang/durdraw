from copy import deepcopy
from durdraw.durdraw_options import Options
import json

class Frame():
    """Frame class - single canvas size frame of animation. a traditional drawing.
    """
    def __init__(self, width, height):
        """ Initialize frame, content[x][y] grid """
        # it's a bunch of rows of ' 'characters.
        self.content = []
        self.colorMap = {}
        self.sizeX = width
        self.sizeY = height
        self.delay = 0  # delay == # of sec to wait at this frame.
        for x in range(0, height):
            self.content.append([])
            for y in range(0, width):
                self.content[x].append(' ')
        self.initColorMap()
        self.setDelayValue(0)

    def setDelayValue(self, delayValue):
        self.delay = delayValue

    def initColorMap(self):
        """ Builds a dictionary mapping X/Y to a FG/BG color pair """
        self.colorMap = {}
        for x in range(0, self.sizeY):
            for y in range(0, self.sizeX):
                self.colorMap.update( {(x,y):(1,0)} )  # tuple keypair (xy), tuple value (fg and bg)

class MovieSettings():  # config, prefs, preferences, etc. Per movie. Separate from AppState options. Formerly Options()
    """ Member variables are canvas X/Y size, Framerate, Video resolution, etc """
    def __init__(self, width=80, height=23):         # default options
        self.framerate = 2.0
        self.sizeX = width
        self.sizeY = height
        #self.saveFileFormat = 4 # save file format version number

class Movie():
    """ Contains an array of Frames, options to add, remove, copy them """
    def __init__(self, opts):
        self.frameCount = 0  # total number of frames
        self.currentFrameNumber = 0
        self.sizeX = opts.sizeX
        self.sizeY = opts.sizeY
        self.frames = []
        self.addEmptyFrame()
        self.currentFrameNumber = self.frameCount
        self.currentFrame = self.frames[self.currentFrameNumber - 1]

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

    def lastMovieLine():
        pass

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)



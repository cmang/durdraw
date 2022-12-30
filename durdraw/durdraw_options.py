import json

class Options():    # config, prefs, preferences, etc. Per movie. Separate from AppState options.
    """ Member variables are canvas X/Y size, Framerate, Video resolution, etc """
    def __init__(self, width=80, height=23):         # default options
        self.framerate = 2.0
        self.sizeX = width
        self.sizeY = height
        self.saveFileFormat = 5 # save file format version number
        # version 4 is pickle, version 5 is JSON
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)


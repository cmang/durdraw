import curses
import time
import pdb
from functools import lru_cache

legacy_256_to_256 = {   # used when loading an old 256 color file in 256 color mode
    #0: 7, # white
    1: 7,    # white
    2: 3,    # cyan
    3: 5,    # magenta
    4: 1,    # blue
    5: 6,    # yellow/brown
    6: 2,    # green
    7: 4,    # red
    8: 16,   # black
    9: 12,   # bright red
    10: 10,  # bright green
    11: 14,  # bright yellow
    12: 9,   # bright blue
    13: 13,  # bright magenta
    14: 11,  # bright cyan
    15: 15,   # bright white
    16: 8,   # bright black
}

legacy_16_to_256 = {   # used when loading an old 16 color file in 256 color mode
    #0: 7, # white
    1: 7,    # white
    2: 3,    # cyan
    3: 5,    # magenta
    4: 1,    # blue
    5: 6,    # yellow/brown
    6: 2,    # green
    7: 4,    # red
    8: 16,   # black
    9: 15,   # bright white
    10: 11,  # bright cyan
    11: 13,  # bright magenta
    12: 9,   # bright blue
    13: 14,  # bright yellow
    14: 10,  # bright green
    15: 12,   # bright red
    16: 8,   # bright black
}

legacy_16_to_16 = {   # used when loading an old 16 color file in 16 color mode
    #0: 7, # white
    1: 8,    # white
    2: 4,    # cyan
    3: 6,    # magenta
    4: 2,    # blue
    5: 7,    # yellow/brown
    6: 3,    # green
    7: 5,    # red
    8: 1,   # black
    9: 16,   # bright white
    10: 12,  # bright cyan
    11: 14,  # bright magenta
    12: 10,   # bright blue
    13: 15,  # bright yellow
    14: 11,  # bright green
    15: 13,   # bright red
    16: 9,   # bright black
    'bg': { # background colors
        1: 7,
        2: 3,    # cyan
        3: 5,    # magenta
        4: 1,    # blue
        5: 6,    # yellow/brown
        6: 2,    # green
        7: 4,    # red
        8: 8,   # black
    }
}

color_256_to_ansi_16 = {   # used when saving a 256 color file, to convert first 16 colors
    #0: 7, # white
    1: 4,    # blue
    2: 2,    # green
    3: 6,    # cyan
    4: 1,    # red
    5: 5,    # magenta
    6: 3,    # yellow
    7: 7,    # white
    8: 8,   # bright black
    9: 12,   # bright blue
    10: 10,  # bright green
    11: 14,  # bright cyan
    12: 9,   # bright red
    13: 13,  # bright magenta
    14: 11,  # bright yellow
    15: 15,   # bright white
    16: 16,   # black
}


mirc_16_to_color_16 = {
    0: 0, # white
    1: 1, # black
    2: 2, # blue
    3: 3,  # green
    10: 4,  # cyan
    5: 5,  # red (brown)
    6: 6,   # magenta
    7: 7,   # yellow (orange)
    15: 8,   # white/grey
    14: 9,   # br black/dark grey
    12: 10, # br blue
    9: 11, # br green
    11: 12, # br cyan
    4: 13,  # br red
    13: 14,  # br magenta
    8: 15,  # br yellow
    #0: 16, # br white
}
    

color_16_to_mirc_16 = {
    0: 0, # white
    1: 1, # black
    2: 2, # blue
    3: 3,  # green
    4: 10,  # cyan
    5: 5,  # red (brown)
    6: 6,   # magenta
    7: 7,   # yellow (orange)
    8: 15,   # white/grey
    9: 14,   # br black/dark grey
    10: 12, # br blue
    11: 9, # br green
    12: 11, # br cyan
    13: 4,  # br red
    14: 13,  # br magenta
    15: 8,  # br yellow
    16: 0, # br white
}

color_256_to_mirc_16 = {
    0: 0, # white
    1: 1, # black
    2: 2, # blue
    3: 3,  # green
    4: 10,  # cyan
    5: 5,  # red (brown)
    6: 6,   # magenta
    7: 7,   # yellow (orange)
    8: 15,   # white/grey
    9: 14,   # br black/dark grey
    10: 12, # br blue
    11: 9, # br green
    12: 11, # br cyan
    13: 4,  # br red
    14: 13,  # br magenta
    15: 8,  # br yellow
    16: 0, # br white
}

ansi_code_to_dur_16_color = {
    '30': 0,  # black
    '31': 5,  # red
    '32': 3,  # green
    '33': 7,  # yellow/brown
    '34': 2,  # blue
    '35': 6,  # magenta
    '36': 4,  # cyan
    '37': 8,  # grey/white

    '90': 9,    # bright black?
    '91': 13,   # bright red?
    '92': 11,   # bright green?
    '93': 15,   # bright yellow
    '94': 10,   # bright blue
    '95': 14,   # bright magenta
    '96': 12,   # bright cyan
    '97': 16,   # bright white

    '40': 0,  # black
    '41': 5,  # red
    '42': 3,  # green
    '43': 7,  # yellow/brown
    '44': 2,  # blue
    '45': 6,  # magenta
    '46': 4,  # cyan
    '47': 8,  # grey/white
}

#ansi_code_to_dur_16_color = {
#    '30': 0,  # black
#    '31': 8,  # white # red
#    '32': 7,  # yellow/brown # green
#    '33': 6,  # magenta # yellow/brown
#    '34': 5,  # red # blue
#    '35': 4,  # cyan # magenta
#    '36': 3,  # green # cyan
#    '37': 2,  # blue # grey/white
#}

class AnsiArtStuff():
    """ Ansi specific stuff.. escape codes, any refs to code page 437, ncurses
        color boilerplate, etc """
    def __init__(self, appState):
        self.appState = appState
        self.colorPairMap = None # fill this with dict of FG/BG -> curses pair #
        self.escapeFgMap = {   # color numbers documented in initColorPairs() comments
            # ANSI escape code FG colors
            # regular colors, white (1) through to black (8 and 0)
            # Using aciddraw/pablodraw-style color order
            0:"0;30",   # 1: black
            1:"0;30",   # 1: black
            2:"0;34",   # 2: blue
            3:"0;32",   # 3: green
            4:"0;36",   # 4: cyan
            5:"0;31",   # 5: red
            6:"0;35",   # 6: magenta
            7:"0;33",   # 7: yellow/brown
            8:"0;37",   # 8: grey/white
            # bright colors
            9:"1;30",   # 9: dark grey/black
            10:"1;34",   # 10 bright blue
            11:"1;32",  # 11 bright green
            12:"1;36",  # cyan
            13:"1;31",  # bright red
            14:"1;35",  # magenta
            15:"1;33",  # yellow
            16:"1;37",  # Bright white
        }
        self.escapeFgMap_old = {   # color numbers documented in initColorPairs() comments
            # ANSI escape code FG colors
            # regular colors, white (1) through to black (8 and 0)
            1:"0;37", 2:"0;36", 3:"0;35", 4:"0;34",
            5:"0;33", 6:"0;32", 7:"0;31", 8:"0;30", 0:"0;30",
            # bright colors, brwhite (9) through to brblack (16)
            9:"1;37", 10:"1;36", 11:"1;35", 12:"1;34",
            13:"1;33", 14:"1;32", 15:"1;31", 16:"1;30"
        }
        self.ansiGraphicsModeTokenMap = {
            """ For parsing ANSI graphics sequence. Eg: ^[0;32;42m is
                green fg (32), magenta bg (42) no bold (0), setting graphics
                mode (m) """
                # expects a function to extract escape sequence then tokenize
                # based on locations of ^[, ; and ending with m.
                # Should this store logical color name strings instead of
                # durdraw color numbers? Then another map can convert names
                # to numbers.
                # * Other ANSI gotchas: Pablodraw uses Cursor Forward (C)
                # commands before each block of characters. Eg: ^[[27C.
                # places a . character at column 27 of the current line.
                # This == different from Durdraw, which would instead place
                # 27 spaces, each escaped to set the color, and then a .
                # character.
            # fg colors
            "37":1, "36":2, "35":3, "34":4, "33":5, "32":6, "31":7, "30":8,
            # bg colors
            "47":1, "46":2, "45":3, "44":4, "43":5, "42":6, "41":7, "40":8,
            # text attributes
            "0":"none",     # non-bold white fg, black bg
            "1":"bold",     # bright color
            "4":"underscore",   # should we handle this?
            "5":"blink",    # iCE color
            "7":"reverse",  # should we handle this?
            "8":"concealed",
        }
        self.escapeBgMap = {
            1: "44",  # blue
            2: "42",  # green
            3: "46",  # cyan
            4: "41",  # red
            5: "45",  # magenta
            6: "43",  # yellow/brown
            7: "47",  # white
            8: "40",  # black
            0: "40",  # black
        }
        self.escapeBgMap_old = {
            1:"47", 2:"46", 3:"45", 4:"44",
            5:"43", 6:"42", 7:"41", 8:"40", 0:"40"
        }

    @lru_cache(maxsize=1024)
    def getColorCode24k(r, g, b):
        """ r, g and b must be numbers between 0-255 """
        return f'\033[38;2;{r};{g};{b}m'

    @lru_cache(maxsize=1024)
    def getColorCodeIrc(self, fg, bg):
        """ Return a string containing the IRC color code to color the next
        character, for given fg/bg """
        # references: https://www.mirc.com/colors.html
        # http://anti.teamidiot.de/static/nei/*/extended_mirc_color_proposal.html
        # map Durdraw -> IRC colors

        if self.appState.colorMode == '16':
            fg = color_16_to_mirc_16[fg]
            bg = color_16_to_mirc_16[bg]
        elif self.appState.colorMode == '256':
            fg = color_256_to_mirc_16[fg]
            bg = color_256_to_mirc_16[bg]
        #    fg = color_256_to_mirc_16[fg]
        #    bg = color_256_to_mirc_16[bg]

        return f'\x03{fg:02d},{bg:02d}'

    @lru_cache(maxsize=1024)
    def getColorCode256(self, fg, bg):
        """ Return a string containing 256-color mode ANSI escape code for
        given fg/bg """
        if fg <= 16 and fg > 0:
            fg = color_256_to_ansi_16[fg]
        return f'\033[38;5;{fg};48;5;{bg}m'

    @lru_cache(maxsize=1024)
    def getColorCode(self, fg, bg):
        """ returns a string containing ANSI escape code for given fg/bg  """
        return f'\033[{self.escapeFgMap[fg]};{self.escapeBgMap[bg]}m'

    def codePage437(self):
        pass

    def convert_colormap(self, mov, conv_table):
        """ takes a dictionary that contains a coler mapper. 
            Modifies the movie
         """    # It might be better to deepclone and return a new movie...
        for frame in mov.frames:
            for line in frame.newColorMap:
                for pair in line:
                    if pair[0] in conv_table.keys():
                        pair[0] = conv_table[pair[0]]
                    if 'bg' in conv_table.keys():
                        if pair[1] in conv_table['bg'].keys():
                            pair[1] = conv_table['bg'][pair[1]]
                    #if pair[1] == 16:
                    #    pair[1] = 0
                    #if pair[1] in conv_table.keys():
                    #    pair[1] = conv_table[pair[1]]

        
    def initColorPairs_general(self, fg_count=256, bg_count=16, use_order=False):   # High color pairs, 256 color
        """ Initialize 256 color mode color pairs """
        self.colorPairMap = {}
        # color order to match thedraw, etc.
        color_order = [0, 4, 2, 6, 1, 5, 3, 7, 8, 12, 10, 14, 9, 13, 11, 15, 16]
        pair = 0
        try:
            curses.use_default_colors()
            bg = 0
            if use_order:
                fg_range = [0, 4, 2, 6, 1, 5, 3, 7, 8, 12, 10, 14, 9, 13, 11, 15]
            else:
                fg_range = list(range(0, fg_count))
            for bg in range(0, bg_count):
                for fg in fg_range:
                    curses.init_pair(pair, fg, bg)
                    #try:
                    #    curses.init_extended_pair(pair, fg, bg)
                    #except Exception as E:
                    #    pdb.set_trace()
                    self.colorPairMap.update({(fg,bg):pair})
                    pair += 1
            self.appState.totalFgColors = fg + 1
            self.appState.totalBgColors = bg + 1
            self.appState.totalFgColors = fg
            self.appState.totalBgColors = bg
            # set pair 0 fg 0 bg to default color:
            self.colorPairMap.update({(0,0):0})
            return True
        except Exception as E:
            #debug_filename = 'debugy.txt'
            #debug_file = open(debug_filename, "w")
            #debug_file.write(str(E))
            #debug_file.close()
            return False

    def initColorPairs_256color(self):   # High color pairs, 256 color
        return self.initColorPairs_general(fg_count=256, bg_count=1)

    def initColorPairs_256color_dead_again(self):   # High color pairs, 256 color
        """ Initialize 256 color mode color pairs """
        self.colorPairMap = {}
        pair = 0
        try:
            curses.use_default_colors()
            bg = 0
            for bg in range(-1, 16):
                for fg in range(0, 256):
                    curses.init_pair(pair, fg, bg)
                    self.colorPairMap.update({(fg,bg):pair})
                    pair += 1
            self.appState.totalFgColors = fg + 1
            self.appState.totalBgColors = bg + 1
            self.appState.totalFgColors = fg
            self.appState.totalBgColors = bg
            # set pair 0 fg 0 bg to default color:
            self.colorPairMap.update({(0,0):0})
            return True
        except Exception as E:
            #debug_filename = 'debugy.txt'
            #debug_file = open(debug_filename, "w")
            #debug_file.write(str(self.colorPairMap))
            #debug_file.close()
            return False

    def initColorPairs_cga(self, trans=False):
        if self.appState.iceColors:
            self.initColorPairs_ice_colors(trans=trans)
        else:
            self.initColorPairs_cga_old2(trans=trans)
        #return self.initColorPairs_general(fg_count=16, bg_count=16, use_order=True)


    #def initColorPairs_ice_colors(self):   # 16 fg colors, 16 bg colors ice colors
    def initColorPairs_ice_colors(self, trans=False):   # 16 fg colors, 16 bg colors
        """ Initialize 16 fg * 16 bg, or 256 color mode color pairs """
        self.colorPairMap = {}
        # default user-friendly color order:
        # black, blue, green, cyan, red, magenta, yellow, white, 16 = nothing?
        if trans:
            defaultBg = -1
        else:
            defaultBg = curses.COLOR_BLACK
        defaultBg = 0
        #defaultBg = curses.COLOR_BLACK
        color_order = [-1, 0, 4, 2, 6, 1, 5, 3, 7, 8, 12, 10, 14, 9, 13, 11, 15, 16]
        bg_order = [0, 4, 2, 6, 1, 5, 3, 7, 8, 12, 10, 14, 9, 13, 11, 15, 16]
        try:
            curses.use_default_colors()
            bg = 0
            map_fg = 0
            map_bg = 0
            #for bg in range(-1, 17):
            #    for fg in range(-1, 17):
            #curses.init_pair(1, curses.COLOR_BLACK, bg) # black - 0
            #self.colorPairMap.update({(curses.COLOR_BLACK,-1):1})
            #curses.init_pair(1, curses.COLOR_BLUE, bg) # blue- 1
            #self.colorPairMap.update({(curses.COLOR_BLUE,bg):2})
            #curses.init_pair(2, curses.COLOR_GREEN, bg) # green - 2
            #self.colorPairMap.update({(curses.COLOR_GREEN,bg):3})
            #curses.init_pair(3, curses.COLOR_CYAN, bg)  # cyan - 3
            #self.colorPairMap.update({(curses.COLOR_CYAN,bg):4})
            #curses.init_pair(4, curses.COLOR_RED, bg) # red - 4
            #self.colorPairMap.update({(curses.COLOR_RED,bg):5})
            #curses.init_pair(5, curses.COLOR_MAGENTA, bg) # magenta/purple - 5
            #self.colorPairMap.update({(curses.COLOR_MAGENTA,bg):6})
            #curses.init_pair(6, curses.COLOR_YELLOW, bg) # brown/yellow - 6
            #self.colorPairMap.update({(curses.COLOR_YELLOW,bg):7})
            #curses.init_pair(7, curses.COLOR_WHITE, bg) # white - 7 (and 0)
            #self.colorPairMap.update({(curses.COLOR_WHITE,bg):8})
            

            # basic ncurses colors - comments for these are durdraw internal color numbers:
            curses.init_pair(0, curses.COLOR_BLACK, defaultBg) # black - 0
            curses.init_pair(1, curses.COLOR_BLUE, defaultBg) # blue- 1
            curses.init_pair(2, curses.COLOR_GREEN, defaultBg) # green - 2
            curses.init_pair(3, curses.COLOR_CYAN, defaultBg)  # cyan - 3
            curses.init_pair(4, curses.COLOR_RED, defaultBg) # red - 4
            curses.init_pair(5, curses.COLOR_MAGENTA, defaultBg) # magenta/purple - 5
            curses.init_pair(6, curses.COLOR_YELLOW, defaultBg) # brown/yellow - 6
            curses.init_pair(7, curses.COLOR_WHITE, defaultBg) # white - 7 (and 0)
            curses.init_pair(8, 7, defaultBg) # white - 7 (and 0)
            self.colorPairMap = {
                # foreground colors, black background
                (0,0):1, (1,0):1, (2,0):2, (3,0):3, (4,0):4, (5,0):5, (6,0):6, (7,0):7, (8,0):8,
                }


            # redo it fro scrarch:
            pair = 0
            #bg += 1
            bg = 0
            for fg in color_order:
                for bg in bg_order:
                    curses.init_pair(pair, fg, bg)
                    self.colorPairMap.update({(map_fg,map_bg):pair})
                    pair += 1
                    map_fg += 1
                map_bg += 1
                map_fg = 0
            self.appState.totalFgColors = fg + 1
            self.appState.totalBgColors = bg + 1
            self.appState.totalFgColors = fg
            self.appState.totalBgColors = bg
            # set pair 0 fg 0 bg to default color:
            self.colorPairMap.update({(0,0):0})
            return True
        except Exception as E:
            #debug_filename = 'debugy.txt'
            #debug_file = open(debug_filename, "w")
            #debug_file.write(str(self.colorPairMap))
            #debug_file.close()
            return False

    def initColorPairs_256color_beta(self):   # High color pairs, 256 color
        """ Initialize 256 color mode color pairs """
        self.colorPairMap = {}
        pair = 1
        try:
            curses.use_default_colors()
            #self.initColorPairs_cga()
            #pair = 58
            #for bg in range(9, 127):
            #    for fg in range(9, curses.COLORS):
            for bg in range(0, 16):
                #for fg in range(0, curses.COLORS):
                for fg in range(0, 255):
                    #debug_write(str(pair))
                    curses.init_pair(pair, fg, bg)
                    self.colorPairMap.update({(fg,bg):pair})
                    pair += 1
                    #self.colorPairMap.update({(fg, bg):pair})
                #curses.init_pair(i + 1, i, -1) # foreground only
            self.appState.totalFgColors = fg
            self.appState.totalBgColors = bg
            return True
        except Exception as E:
            #debug_filename = 'debugy.txt'
            #debug_file = open(debug_filename, "w")
            #debug_file.write(str(self.colorPairMap))
            #debug_file.close()
            return False


    def initColorPairs_cga_old2(self, trans=False):
        """ Setup ncurses color pairs for ANSI colors """
        # this kind of hurts to write. wtf, ncurses.
        if trans:
            defaultBg = -1
        else:
            defaultBg = curses.COLOR_BLACK
        # basic ncurses colors - comments for these are durdraw internal color numbers:
        curses.init_pair(1, curses.COLOR_BLACK, defaultBg) # black - 0
        curses.init_pair(2, curses.COLOR_BLUE, defaultBg) # blue- 1
        curses.init_pair(3, curses.COLOR_GREEN, defaultBg) # green - 2
        curses.init_pair(4, curses.COLOR_CYAN, defaultBg)  # cyan - 3
        curses.init_pair(5, curses.COLOR_RED, defaultBg) # red - 4
        curses.init_pair(6, curses.COLOR_MAGENTA, defaultBg) # magenta/purple - 5
        curses.init_pair(7, curses.COLOR_YELLOW, defaultBg) # brown/yellow - 6
        curses.init_pair(8, curses.COLOR_WHITE, defaultBg) # white - 7 (and 0)
        # black with background colors
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_BLUE) # 1,2
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_GREEN) # 1,3
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_CYAN)  # 1,4
        curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_RED)  # 1,5
        curses.init_pair(13, curses.COLOR_BLACK, curses.COLOR_MAGENTA) # 1,6
        curses.init_pair(14, curses.COLOR_BLACK, curses.COLOR_YELLOW)   # 1,7
        curses.init_pair(15, curses.COLOR_BLACK, curses.COLOR_WHITE)   # 1,8
        # blue with background colors
        curses.init_pair(16, curses.COLOR_BLUE, curses.COLOR_BLUE) # 2,2
        curses.init_pair(17, curses.COLOR_BLUE, curses.COLOR_GREEN) # 2,3
        curses.init_pair(18, curses.COLOR_BLUE, curses.COLOR_CYAN)  # 2,4
        curses.init_pair(19, curses.COLOR_BLUE, curses.COLOR_RED)  # 2,5
        curses.init_pair(20, curses.COLOR_BLUE, curses.COLOR_MAGENTA) # 2,6
        curses.init_pair(21, curses.COLOR_BLUE, curses.COLOR_YELLOW)   # 2,7
        curses.init_pair(22, curses.COLOR_BLUE, curses.COLOR_WHITE)   # 2,7
        # green with background colors
        curses.init_pair(23, curses.COLOR_GREEN, curses.COLOR_BLUE) # 3,1
        curses.init_pair(24, curses.COLOR_GREEN, curses.COLOR_GREEN) # 3,2
        curses.init_pair(25, curses.COLOR_GREEN, curses.COLOR_CYAN) # 3,3
        curses.init_pair(26, curses.COLOR_GREEN, curses.COLOR_RED)  # 3,4
        curses.init_pair(27, curses.COLOR_GREEN, curses.COLOR_MAGENTA)  # 3,5
        curses.init_pair(28, curses.COLOR_GREEN, curses.COLOR_YELLOW) # 3,6
        curses.init_pair(29, curses.COLOR_GREEN, curses.COLOR_WHITE)   # 3,7
        # cyan with background colors
        curses.init_pair(30, curses.COLOR_CYAN, curses.COLOR_BLUE) # 4,1
        curses.init_pair(31, curses.COLOR_CYAN, curses.COLOR_GREEN) # 4,2
        curses.init_pair(32, curses.COLOR_CYAN, curses.COLOR_CYAN) # 4,3
        curses.init_pair(33, curses.COLOR_CYAN, curses.COLOR_RED)  # 4,4
        curses.init_pair(34, curses.COLOR_CYAN, curses.COLOR_MAGENTA)  # 4,5
        curses.init_pair(35, curses.COLOR_CYAN, curses.COLOR_YELLOW) # 4,6
        curses.init_pair(36, curses.COLOR_CYAN, curses.COLOR_WHITE)   # 4,7
        # yellow with background colors
        curses.init_pair(37, curses.COLOR_RED, curses.COLOR_BLUE) # 5,1
        curses.init_pair(38, curses.COLOR_RED, curses.COLOR_GREEN) # 5,2
        curses.init_pair(39, curses.COLOR_RED, curses.COLOR_CYAN) # 5,3
        curses.init_pair(40, curses.COLOR_RED, curses.COLOR_RED)  # 5,4
        curses.init_pair(41, curses.COLOR_RED, curses.COLOR_MAGENTA)  # 5,5
        curses.init_pair(42, curses.COLOR_RED, curses.COLOR_YELLOW) # 5,6
        curses.init_pair(43, curses.COLOR_RED, curses.COLOR_WHITE)   # 5,7
        # green with background colors
        curses.init_pair(44, curses.COLOR_MAGENTA, curses.COLOR_BLUE) # 6,1
        curses.init_pair(45, curses.COLOR_MAGENTA, curses.COLOR_GREEN) # 6,2
        curses.init_pair(46, curses.COLOR_MAGENTA, curses.COLOR_CYAN) # 6,3
        curses.init_pair(47, curses.COLOR_MAGENTA, curses.COLOR_RED)  # 6,4
        curses.init_pair(48, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)  # 6,5
        curses.init_pair(49, curses.COLOR_MAGENTA, curses.COLOR_YELLOW) # 6,6
        curses.init_pair(50, curses.COLOR_MAGENTA, curses.COLOR_WHITE)   # 6,7
        # red with background colors
        curses.init_pair(51, curses.COLOR_YELLOW, curses.COLOR_BLUE) # 7,1
        curses.init_pair(52, curses.COLOR_YELLOW, curses.COLOR_GREEN) # 7,2
        curses.init_pair(53, curses.COLOR_YELLOW, curses.COLOR_CYAN) # 7,3
        curses.init_pair(54, curses.COLOR_YELLOW, curses.COLOR_RED)  # 7,4
        curses.init_pair(55, curses.COLOR_YELLOW, curses.COLOR_MAGENTA)  # 7,5
        curses.init_pair(56, curses.COLOR_YELLOW, curses.COLOR_YELLOW) # 7,6
        curses.init_pair(57, curses.COLOR_YELLOW, curses.COLOR_WHITE)   # 7,7
        # black with background colors
        curses.init_pair(58, curses.COLOR_WHITE, curses.COLOR_BLUE) # 8,1
        curses.init_pair(59, curses.COLOR_WHITE, curses.COLOR_GREEN) # 8,2
        curses.init_pair(60, curses.COLOR_WHITE, curses.COLOR_CYAN) # 8,3
        curses.init_pair(61, curses.COLOR_WHITE, curses.COLOR_RED)  # 8,4
        curses.init_pair(62, curses.COLOR_WHITE, curses.COLOR_MAGENTA)  # 8,5
        curses.init_pair(63, curses.COLOR_WHITE, curses.COLOR_YELLOW) # 8,6
        curses.init_pair(64, curses.COLOR_WHITE, curses.COLOR_WHITE)   # 8,7
        #curses.init_pair(64, defaultBg, curses.COLOR_RED)   # 8,7
        # ^ this doesn't work ?!@ ncurses pair # must be between 1 and 63
        # or ncurses (const?) COLOR_PAIR - 1 
        # fix is: have functions to swap color map from blackfg to normal.
        # call that function when drawing if the fg color == black, then switch back
        # after each character. Or.. keep track which map we're in in a variable.
        self.colorPairMap = {
             # foreground colors, black background
             (0,0):1, (1,0):1, (2,0):2, (3,0):3, (4,0):4, (5,0):5, (6,0):6, (7,0):7, (8,0):8,
             # and again, because black == both 0 and 8. :| let's just ditch 0?
             (0,8):1, (1,8):1, (2,8):2, (3,8):3, (4,8):4, (5,8):5, (6,8):6, (7,8):7, (8,8):8,
             # white with backround colors 
             (1,1):9, (1,2):10, (1,3):11, (1,4):12, (1,5):13, (1,6):14, (1,7):15,
             # cyan with backround colors 
             (2,1):16, (2,2):17, (2,3):18, (2,4):19, (2,5):20, (2,6):21, (2,7):22,
             # magenta with background colors
             (3,1):23, (3,2):24, (3,3):25, (3,4):26, (3,5):27, (3,6):28, (3,7):29,
             # blue with background colors
             (4,1):30, (4,2):31, (4,3):32, (4,4):33, (4,5):34, (4,6):35, (4,7):36,
             # yellow with background colors
             (5,1):37, (5,2):38, (5,3):39, (5,4):40, (5,5):41, (5,6):42, (5,7):43,
             # green with background colors
             (6,1):44, (6,2):45, (6,3):46, (6,4):47, (6,5):48, (6,6):49, (6,7):50,
             # red with background colors
             (7,1):51, (7,2):52, (7,3):53, (7,4):54, (7,5):55, (7,6):56, (7,7):57,
             # black with background colors
             (8,1):58, (8,2):59, (8,3):60, (8,4):61, (8,5):62, (8,6):63, 
             #(8,7):57,  # 57 instead of 64, because we switch color maps for black
             # on red
             (8,7):64, 
             # Again, this time with feeling
             (0,1):58, (0,2):59, (0,3):60, (0,4):61, (0,5):62, (0,6):63, 
             (0,7):57,  
             # BRIGHT COLORS 9-16
             # white with backround colors 
             (9,0):1, (9,8):1, (9,1):9, (9,2):10, (9,3):11, (9,4):12, (9,5):13, (9,6):14, (9,7):15,
             # cyan with backround colors 
             (10,0):2, (10,8):2, (10,1):16, (10,2):17, (10,3):18, (10,4):19, (10,5):20, (10,6):21, (10,7):22,
             # magenta with background colors
             (11,0):3, (11,8):3, (11,1):23, (11,2):24, (11,3):25, (11,4):26, (11,5):27, (11,6):28, (11,7):29,
             # blue with background colors
             (12,0):4, (12,8):4, (12,1):30, (12,2):31, (12,3):32, (12,4):33, (12,5):34, (12,6):35, (12,7):36,
             # yellow with background colors
             (13,0):5, (13,8):5, (13,1):37, (13,2):38, (13,3):39, (13,4):40, (13,5):41, (13,6):42, (13,7):43,
             # green with background colors
             (14,0):6, (14,8):6, (14,1):44, (14,2):45, (14,3):46, (14,4):47, (14,5):48, (14,6):49, (14,7):50,
             # red with background colors
             (15,0):7, (15,8):7, (15,1):51, (15,2):52, (15,3):53, (15,4):54, (15,5):55, (15,6):56, (15,7):57,
             # black with background colors
             (16,0):8, (16,8):8, (16,1):58, (16,2):59, (16,3):60, (16,4):61, (16,5):62, (16,6):63, 
             #(16,7):57,  # 57 instead of 64, because we switch color maps for black
             (16,7):64,  
             } # (fg,bg):cursespair

    def initColorPairs_cga_old(self):
       """ Setup ncurses color pairs for ANSI colors """
       # this kind of hurts to write. wtf, ncurses.
       # basic ncurses colors - comments for these are durdraw internal color numbers:
       curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # white - 1
       curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # cyan - 2
       curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # magenta - 3
       curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)  # blue - 4
       curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # yellow - 5
       curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK) # green - 6
       curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK) # red - 7
       curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_BLACK) # black - 8 (and 0)
       # white with background colors
       curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_WHITE) # 1,1
       curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_CYAN) # 1,2
       curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_MAGENTA) # 1,3
       curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_BLUE)  # 1,4
       curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_YELLOW)  # 1,5
       curses.init_pair(14, curses.COLOR_WHITE, curses.COLOR_GREEN) # 1,6
       curses.init_pair(15, curses.COLOR_WHITE, curses.COLOR_RED)   # 1,7
       # cyan with background colors
       curses.init_pair(16, curses.COLOR_CYAN, curses.COLOR_WHITE) # 2,1
       curses.init_pair(17, curses.COLOR_CYAN, curses.COLOR_CYAN) # 2,2
       curses.init_pair(18, curses.COLOR_CYAN, curses.COLOR_MAGENTA) # 2,3
       curses.init_pair(19, curses.COLOR_CYAN, curses.COLOR_BLUE)  # 2,4
       curses.init_pair(20, curses.COLOR_CYAN, curses.COLOR_YELLOW)  # 2,5
       curses.init_pair(21, curses.COLOR_CYAN, curses.COLOR_GREEN) # 2,6
       curses.init_pair(22, curses.COLOR_CYAN, curses.COLOR_RED)   # 2,7
       # magenta with background colors
       curses.init_pair(23, curses.COLOR_MAGENTA, curses.COLOR_WHITE) # 3,1
       curses.init_pair(24, curses.COLOR_MAGENTA, curses.COLOR_CYAN) # 3,2
       curses.init_pair(25, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA) # 3,3
       curses.init_pair(26, curses.COLOR_MAGENTA, curses.COLOR_BLUE)  # 3,4
       curses.init_pair(27, curses.COLOR_MAGENTA, curses.COLOR_YELLOW)  # 3,5
       curses.init_pair(28, curses.COLOR_MAGENTA, curses.COLOR_GREEN) # 3,6
       curses.init_pair(29, curses.COLOR_MAGENTA, curses.COLOR_RED)   # 3,7
       # blue with background colors
       curses.init_pair(30, curses.COLOR_BLUE, curses.COLOR_WHITE) # 4,1
       curses.init_pair(31, curses.COLOR_BLUE, curses.COLOR_CYAN) # 4,2
       curses.init_pair(32, curses.COLOR_BLUE, curses.COLOR_MAGENTA) # 4,3
       curses.init_pair(33, curses.COLOR_BLUE, curses.COLOR_BLUE)  # 4,4
       curses.init_pair(34, curses.COLOR_BLUE, curses.COLOR_YELLOW)  # 4,5
       curses.init_pair(35, curses.COLOR_BLUE, curses.COLOR_GREEN) # 4,6
       curses.init_pair(36, curses.COLOR_BLUE, curses.COLOR_RED)   # 4,7
       # yellow with background colors
       curses.init_pair(37, curses.COLOR_YELLOW, curses.COLOR_WHITE) # 5,1
       curses.init_pair(38, curses.COLOR_YELLOW, curses.COLOR_CYAN) # 5,2
       curses.init_pair(39, curses.COLOR_YELLOW, curses.COLOR_MAGENTA) # 5,3
       curses.init_pair(40, curses.COLOR_YELLOW, curses.COLOR_BLUE)  # 5,4
       curses.init_pair(41, curses.COLOR_YELLOW, curses.COLOR_YELLOW)  # 5,5
       curses.init_pair(42, curses.COLOR_YELLOW, curses.COLOR_GREEN) # 5,6
       curses.init_pair(43, curses.COLOR_YELLOW, curses.COLOR_RED)   # 5,7
       # green with background colors
       curses.init_pair(44, curses.COLOR_GREEN, curses.COLOR_WHITE) # 6,1
       curses.init_pair(45, curses.COLOR_GREEN, curses.COLOR_CYAN) # 6,2
       curses.init_pair(46, curses.COLOR_GREEN, curses.COLOR_MAGENTA) # 6,3
       curses.init_pair(47, curses.COLOR_GREEN, curses.COLOR_BLUE)  # 6,4
       curses.init_pair(48, curses.COLOR_GREEN, curses.COLOR_YELLOW)  # 6,5
       curses.init_pair(49, curses.COLOR_GREEN, curses.COLOR_GREEN) # 6,6
       curses.init_pair(50, curses.COLOR_GREEN, curses.COLOR_RED)   # 6,7
       # red with background colors
       curses.init_pair(51, curses.COLOR_RED, curses.COLOR_WHITE) # 7,1
       curses.init_pair(52, curses.COLOR_RED, curses.COLOR_CYAN) # 7,2
       curses.init_pair(53, curses.COLOR_RED, curses.COLOR_MAGENTA) # 7,3
       curses.init_pair(54, curses.COLOR_RED, curses.COLOR_BLUE)  # 7,4
       curses.init_pair(55, curses.COLOR_RED, curses.COLOR_YELLOW)  # 7,5
       curses.init_pair(56, curses.COLOR_RED, curses.COLOR_GREEN) # 7,6
       #curses.init_pair(57, curses.COLOR_RED, curses.COLOR_RED)   # 7,7
       # black with background colors
       curses.init_pair(58, curses.COLOR_BLACK, curses.COLOR_WHITE) # 8,1
       curses.init_pair(59, curses.COLOR_BLACK, curses.COLOR_CYAN) # 8,2
       curses.init_pair(60, curses.COLOR_BLACK, curses.COLOR_MAGENTA) # 8,3
       curses.init_pair(61, curses.COLOR_BLACK, curses.COLOR_BLUE)  # 8,4
       curses.init_pair(62, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # 8,5
       curses.init_pair(63, curses.COLOR_BLACK, curses.COLOR_GREEN) # 8,6
       curses.init_pair(57, curses.COLOR_BLACK, curses.COLOR_RED)   # 8,7
       #curses.init_pair(64, curses.COLOR_BLACK, curses.COLOR_RED)   # 8,7
       # ^ this doesn't work ?!@ ncurses pair # must be between 1 and 63
       # or ncurses (const?) COLOR_PAIR - 1 
       # fix is: have functions to swap color map from blackfg to normal.
       # call that function when drawing if the fg color == black, then switch back
       # after each character. Or.. keep track which map we're in in a variable.
       self.colorPairMap = {
            # foreground colors, black background
            (0,0):1, (1,0):1, (2,0):2, (3,0):3, (4,0):4, (5,0):5, (6,0):6, (7,0):7, (8,0):8,
            # and again, because black == both 0 and 8. :| let's just ditch 0?
            (0,8):1, (1,8):1, (2,8):2, (3,8):3, (4,8):4, (5,8):5, (6,8):6, (7,8):7, (8,8):8,
            # white with backround colors 
            (1,1):9, (1,2):10, (1,3):11, (1,4):12, (1,5):13, (1,6):14, (1,7):15,
            # cyan with backround colors 
            (2,1):16, (2,2):17, (2,3):18, (2,4):19, (2,5):20, (2,6):21, (2,7):22,
            # magenta with background colors
            (3,1):23, (3,2):24, (3,3):25, (3,4):26, (3,5):27, (3,6):28, (3,7):29,
            # blue with background colors
            (4,1):30, (4,2):31, (4,3):32, (4,4):33, (4,5):34, (4,6):35, (4,7):36,
            # yellow with background colors
            (5,1):37, (5,2):38, (5,3):39, (5,4):40, (5,5):41, (5,6):42, (5,7):43,
            # green with background colors
            (6,1):44, (6,2):45, (6,3):46, (6,4):47, (6,5):48, (6,6):49, (6,7):50,
            # red with background colors
            (7,1):51, (7,2):52, (7,3):53, (7,4):54, (7,5):55, (7,6):56, (7,7):57,
            # black with background colors
            (8,1):58, (8,2):59, (8,3):60, (8,4):61, (8,5):62, (8,6):63, 
            (8,7):57,  # 57 instead of 64, because we switch color maps for black
            # on red
            # BRIGHT COLORS 9-16
            # white with backround colors 
            (9,0):1, (9,8):1, (9,1):9, (9,2):10, (9,3):11, (9,4):12, (9,5):13, (9,6):14, (9,7):15,
            # cyan with backround colors 
            (10,0):2, (10,8):2, (10,1):16, (10,2):17, (10,3):18, (10,4):19, (10,5):20, (10,6):21, (10,7):22,
            # magenta with background colors
            (11,0):3, (11,8):3, (11,1):23, (11,2):24, (11,3):25, (11,4):26, (11,5):27, (11,6):28, (11,7):29,
            # blue with background colors
            (12,0):4, (12,8):4, (12,1):30, (12,2):31, (12,3):32, (12,4):33, (12,5):34, (12,6):35, (12,7):36,
            # yellow with background colors
            (13,0):5, (13,8):5, (13,1):37, (13,2):38, (13,3):39, (13,4):40, (13,5):41, (13,6):42, (13,7):43,
            # green with background colors
            (14,0):6, (14,8):6, (14,1):44, (14,2):45, (14,3):46, (14,4):47, (14,5):48, (14,6):49, (14,7):50,
            # red with background colors
            (15,0):7, (15,8):7, (15,1):51, (15,2):52, (15,3):53, (15,4):54, (15,5):55, (15,6):56, (15,7):57,
            # black with background colors
            (16,0):8, (16,8):8, (16,1):58, (16,2):59, (16,3):60, (16,4):61, (16,5):62, (16,6):63, 
            (16,7):57,  # 57 instead of 64, because we switch color maps for black
            } # (fg,bg):cursespair



    def initColorPairs(self):
       """ Setup ncurses color pairs for ANSI colors """
       # this kind of hurts to write. wtf, ncurses.
       # basic ncurses colors - comments for these are durdraw internal color numbers:
       curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # white - 1
       curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # cyan - 2
       curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # magenta - 3
       curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)  # blue - 4
       curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # yellow - 5
       curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK) # green - 6
       curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK) # red - 7
       curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_BLACK) # black - 8 (and 0)
       # white with background colors
       curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_WHITE) # 1,1
       curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_CYAN) # 1,2
       curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_MAGENTA) # 1,3
       curses.init_pair(12, curses.COLOR_WHITE, curses.COLOR_BLUE)  # 1,4
       curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_YELLOW)  # 1,5
       curses.init_pair(14, curses.COLOR_WHITE, curses.COLOR_GREEN) # 1,6
       curses.init_pair(15, curses.COLOR_WHITE, curses.COLOR_RED)   # 1,7
       # cyan with background colors
       curses.init_pair(16, curses.COLOR_CYAN, curses.COLOR_WHITE) # 2,1
       curses.init_pair(17, curses.COLOR_CYAN, curses.COLOR_CYAN) # 2,2
       curses.init_pair(18, curses.COLOR_CYAN, curses.COLOR_MAGENTA) # 2,3
       curses.init_pair(19, curses.COLOR_CYAN, curses.COLOR_BLUE)  # 2,4
       curses.init_pair(20, curses.COLOR_CYAN, curses.COLOR_YELLOW)  # 2,5
       curses.init_pair(21, curses.COLOR_CYAN, curses.COLOR_GREEN) # 2,6
       curses.init_pair(22, curses.COLOR_CYAN, curses.COLOR_RED)   # 2,7
       # magenta with background colors
       curses.init_pair(23, curses.COLOR_MAGENTA, curses.COLOR_WHITE) # 3,1
       curses.init_pair(24, curses.COLOR_MAGENTA, curses.COLOR_CYAN) # 3,2
       curses.init_pair(25, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA) # 3,3
       curses.init_pair(26, curses.COLOR_MAGENTA, curses.COLOR_BLUE)  # 3,4
       curses.init_pair(27, curses.COLOR_MAGENTA, curses.COLOR_YELLOW)  # 3,5
       curses.init_pair(28, curses.COLOR_MAGENTA, curses.COLOR_GREEN) # 3,6
       curses.init_pair(29, curses.COLOR_MAGENTA, curses.COLOR_RED)   # 3,7
       # blue with background colors
       curses.init_pair(30, curses.COLOR_BLUE, curses.COLOR_WHITE) # 4,1
       curses.init_pair(31, curses.COLOR_BLUE, curses.COLOR_CYAN) # 4,2
       curses.init_pair(32, curses.COLOR_BLUE, curses.COLOR_MAGENTA) # 4,3
       curses.init_pair(33, curses.COLOR_BLUE, curses.COLOR_BLUE)  # 4,4
       curses.init_pair(34, curses.COLOR_BLUE, curses.COLOR_YELLOW)  # 4,5
       curses.init_pair(35, curses.COLOR_BLUE, curses.COLOR_GREEN) # 4,6
       curses.init_pair(36, curses.COLOR_BLUE, curses.COLOR_RED)   # 4,7
       # yellow with background colors
       curses.init_pair(37, curses.COLOR_YELLOW, curses.COLOR_WHITE) # 5,1
       curses.init_pair(38, curses.COLOR_YELLOW, curses.COLOR_CYAN) # 5,2
       curses.init_pair(39, curses.COLOR_YELLOW, curses.COLOR_MAGENTA) # 5,3
       curses.init_pair(40, curses.COLOR_YELLOW, curses.COLOR_BLUE)  # 5,4
       curses.init_pair(41, curses.COLOR_YELLOW, curses.COLOR_YELLOW)  # 5,5
       curses.init_pair(42, curses.COLOR_YELLOW, curses.COLOR_GREEN) # 5,6
       curses.init_pair(43, curses.COLOR_YELLOW, curses.COLOR_RED)   # 5,7
       # green with background colors
       curses.init_pair(44, curses.COLOR_GREEN, curses.COLOR_WHITE) # 6,1
       curses.init_pair(45, curses.COLOR_GREEN, curses.COLOR_CYAN) # 6,2
       curses.init_pair(46, curses.COLOR_GREEN, curses.COLOR_MAGENTA) # 6,3
       curses.init_pair(47, curses.COLOR_GREEN, curses.COLOR_BLUE)  # 6,4
       curses.init_pair(48, curses.COLOR_GREEN, curses.COLOR_YELLOW)  # 6,5
       curses.init_pair(49, curses.COLOR_GREEN, curses.COLOR_GREEN) # 6,6
       curses.init_pair(50, curses.COLOR_GREEN, curses.COLOR_RED)   # 6,7
       # red with background colors
       curses.init_pair(51, curses.COLOR_RED, curses.COLOR_WHITE) # 7,1
       curses.init_pair(52, curses.COLOR_RED, curses.COLOR_CYAN) # 7,2
       curses.init_pair(53, curses.COLOR_RED, curses.COLOR_MAGENTA) # 7,3
       curses.init_pair(54, curses.COLOR_RED, curses.COLOR_BLUE)  # 7,4
       curses.init_pair(55, curses.COLOR_RED, curses.COLOR_YELLOW)  # 7,5
       curses.init_pair(56, curses.COLOR_RED, curses.COLOR_GREEN) # 7,6
       #curses.init_pair(57, curses.COLOR_RED, curses.COLOR_RED)   # 7,7
       # black with background colors
       # black with background colors
       curses.init_pair(58, curses.COLOR_BLACK, curses.COLOR_WHITE) # 8,1
       curses.init_pair(59, curses.COLOR_BLACK, curses.COLOR_CYAN) # 8,2
       curses.init_pair(60, curses.COLOR_BLACK, curses.COLOR_MAGENTA) # 8,3
       curses.init_pair(61, curses.COLOR_BLACK, curses.COLOR_BLUE)  # 8,4
       curses.init_pair(62, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # 8,5
       curses.init_pair(63, curses.COLOR_BLACK, curses.COLOR_GREEN) # 8,6
       curses.init_pair(57, curses.COLOR_BLACK, curses.COLOR_RED)   # 8,7
       #curses.init_pair(64, curses.COLOR_BLACK, curses.COLOR_RED)   # 8,7
       # ^ this doesn't work ?!@ ncurses pair # must be between 1 and 63
       # or ncurses (const?) COLOR_PAIR - 1
       # fix is: have functions to swap color map from blackfg to normal.
       # call that function when drawing if the fg color == black, then switch back
       # after each character. Or.. keep track which map we're in in a variable.
       self.colorPairMap = {
            # foreground colors, black background
            (0,0):1, (1,0):1, (2,0):2, (3,0):3, (4,0):4, (5,0):5, (6,0):6, (7,0):7, (8,0):8,
            # and again, because black == both 0 and 8. :| let's just ditch 0?
            (0,8):1, (1,8):1, (2,8):2, (3,8):3, (4,8):4, (5,8):5, (6,8):6, (7,8):7, (8,8):8,
            # white with backround colors
            (1,1):9, (1,2):10, (1,3):11, (1,4):12, (1,5):13, (1,6):14, (1,7):15,
            # cyan with backround colors
            (2,1):16, (2,2):17, (2,3):18, (2,4):19, (2,5):20, (2,6):21, (2,7):22,
            # magenta with background colors
            (3,1):23, (3,2):24, (3,3):25, (3,4):26, (3,5):27, (3,6):28, (3,7):29,
            # blue with background colors
            (4,1):30, (4,2):31, (4,3):32, (4,4):33, (4,5):34, (4,6):35, (4,7):36,
            # yellow with background colors
            (5,1):37, (5,2):38, (5,3):39, (5,4):40, (5,5):41, (5,6):42, (5,7):43,
            # green with background colors
            (6,1):44, (6,2):45, (6,3):46, (6,4):47, (6,5):48, (6,6):49, (6,7):50,
            # red with background colors
            (7,1):51, (7,2):52, (7,3):53, (7,4):54, (7,5):55, (7,6):56, (7,7):57,
            # black with background colors
            (8,1):58, (8,2):59, (8,3):60, (8,4):61, (8,5):62, (8,6):63,
            (8,7):57,  # 57 instead of 64, because we switch color maps for black
            # on red
            # BRIGHT COLORS 9-16
            # white with backround colors
            (9,0):1, (9,8):1, (9,1):9, (9,2):10, (9,3):11, (9,4):12, (9,5):13, (9,6):14, (9,7):15,
            # cyan with backround colors
            (10,0):2, (10,8):2, (10,1):16, (10,2):17, (10,3):18, (10,4):19, (10,5):20, (10,6):21, (10,7):22,
            # magenta with background colors
            (11,0):3, (11,8):3, (11,1):23, (11,2):24, (11,3):25, (11,4):26, (11,5):27, (11,6):28, (11,7):29,
            # blue with background colors
            (12,0):4, (12,8):4, (12,1):30, (12,2):31, (12,3):32, (12,4):33, (12,5):34, (12,6):35, (12,7):36,
            # yellow with background colors
            (13,0):5, (13,8):5, (13,1):37, (13,2):38, (13,3):39, (13,4):40, (13,5):41, (13,6):42, (13,7):43,
            # green with background colors
            (14,0):6, (14,8):6, (14,1):44, (14,2):45, (14,3):46, (14,4):47, (14,5):48, (14,6):49, (14,7):50,
            # red with background colors
            (15,0):7, (15,8):7, (15,1):51, (15,2):52, (15,3):53, (15,4):54, (15,5):55, (15,6):56, (15,7):57,
            # black with background colors
            (16,0):8, (16,8):8, (16,1):58, (16,2):59, (16,3):60, (16,4):61, (16,5):62, (16,6):63,
            (16,7):57,  # 57 instead of 64, because we switch color maps for black
            } # (fg,bg):cursespair



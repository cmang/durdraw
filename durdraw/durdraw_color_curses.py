import curses
import time
import pdb

class AnsiArtStuff():
    """ Ansi specific stuff.. escape codes, any refs to code page 437, ncurses
        color boilerplate, etc """
    def __init__(self):
        self.ColorPairMap = None # fill this with dict of FG/BG -> curses pair #
        self.escapeFgMap = {   # color numbers documented in initColorPairs() comments
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
            1:"47", 2:"46", 3:"45", 4:"44",
            5:"43", 6:"42", 7:"41", 8:"40", 0:"40"
        }

    def getColorCode24k(r, g, b):
        """ r, g and b must be numbers between 0-255 """
        code = '\033[38;2;'
        code += str(r) + ';' + str(g) + ';' + str(b)
        code += 'm'
        return code

    def getColorCodeIrc(self, fg, bg):
        """ Return a string containing the IRC coolor code to color the next
        character, for given fg/bg """
        # references: https://www.mirc.com/colors.html
        # http://anti.teamidiot.de/static/nei/*/extended_mirc_color_proposal.html
        # map Durdraw -> IRC colors
        colorMap16color = { 0: 1, # black
                            1: 15, # grey
                            2: 10, # cyan
                            3: 6,   # purple
                            4: 2,   # blue
                            5: 7,   # brown
                            6: 3,   # green
                            7: 5,   # red
                            8: 1,   # black
                            9: 0,   # white/brwhite
                            10: 11, # br cyan
                            11: 13, # br purple
                            12: 12, # br blue
                            13: 8,  # br yellow
                            14: 9,  # br green
                            15: 4,  # br red
                            16: 14, # br black/dark grey
                            }
        fg = colorMap16color[fg]
        bg = colorMap16color[bg]

        # build the code
        code = '\x03'
        #code = code + str(fg)
        code = code + f'{fg:02d}'
        code = code + ','
        #code = code + str(bg)
        code = code + f'{bg:02d}'
        # code = code + '\x03'
        return code

    def getColorCode256(self, fg, bg):
        """ Return a string containing 256-color mode ANSI escape code for
        given fg/bg """
        code = '\033[38;5;'    # begin escape sequence
        code = code + str(fg)
        code = code + ';'
        #code = code + '48;5;'
        #code = code + str(bg)
        #code = code + str('0')
        code = code + 'm'
        return code

    def getColorCode(self, fg, bg):
        """ returns a string containing ANSI escape code for given fg/bg  """
        escape = '\033['    # begin escape sequence
        escape = escape + self.escapeFgMap[fg] + ';'  # set fg color
        escape = escape + self.escapeBgMap[bg]  # set bg color
        escape = escape + "m"   # m = set graphics mode command
        return escape

    def codePage437(self):
        pass

    def initColorPairs_hicolor(self):   # High color pairs, 256 color
        """ Initialize 256 color mode color pairs """
        self.colorPairMap = {}
        pair = 0
        try:
            curses.use_default_colors()
            #self.initColorPairs_cga()
            #pair = 58
            #for bg in range(9, 127):
            #    for fg in range(9, curses.COLORS):
            for bg in range(0, 127):
                for fg in range(0, curses.COLORS):
                #for fg in range(0, 127):
                    #debug_write(str(pair))
                    curses.init_pair(pair, fg, bg)
                    self.colorPairMap.update({(fg,bg):pair})
                    pair += 1
                    #self.colorPairMap.update({(fg, bg):pair})
                #curses.init_pair(i + 1, i, -1) # foreground only
            return True
        except Exception as E:
            return False
            #print(f"Error initializing color pair {pair}: {E}")
            #print(str(curses.COLORS))
            #time.sleep(3)
            #pdb.set_trace();

    def initColorPairs_cga(self):
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
    def switchColorMap(self, map=0):    # deprecated?  I think so.
            if (map == 1):   # 1 = black map.. deal with it. pair 57 == black on red.
                # black with background colors
                curses.init_pair(57, curses.COLOR_BLACK, curses.COLOR_RED)   # 8,7
            elif (map == 0):  # 0 = normal color map, pair 57 == red on red
                curses.init_pair(57, curses.COLOR_RED, curses.COLOR_RED)   # 7,7



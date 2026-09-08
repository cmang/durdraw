import pathlib
import pdb
import struct

durdraw_plugin_version = 1

# Plugin information
durdraw_plugin = {
    "name": "MS-DOS .COM File",
    "author": "",
    "version":  1,   # Plugin verison, if applicable
    "provides": ["transform_movie", "export_movie"],
    "type": ["export"],
    "desc": "Exports frame to 16-bit MS-DOS .COM file"
}

opts  = {
    "file name": "ansi.com"
}

# CGA/VGA colors as they appear in video RAM (color textmode)
cga_fg_colors = {
    'black':     0b00000000,
    'blue':      0b00000001,
    'green':     0b00000010,
    'cyan':      0b00000011,
    'red':       0b00000100,
    'magenta':   0b00000101,
    'brown':     0b00000110,
    'white':     0b00000111,
    'br_black':     0b00001000,
    'br_blue':      0b00001001,
    'br_green':     0b00001010,
    'br_cyan':      0b00001011,
    'br_red':       0b00001100,
    'br_magenta':   0b00001101,
    'br_brown':     0b00001110,
    'br_white':     0b00001111,
}

cga_bg_colors = {
    'black':     0b00000000,
    'blue':      0b00010000,
    'green':     0b00100000,
    'cyan':      0b00110000,
    'red':       0b01000000,
    'magenta':   0b01010000,
    'brown':     0b01100000,
    'white':     0b01110000,
}

durdraw_colors_16 = {
    0: 'black',
    1: 'black',
    2: 'blue',
    3: 'green',
    4: 'cyan',
    5: 'red',
    6: 'magenta',
    7: 'brown',
    8: 'white',
    9: 'br_black',
    10: 'br_blue',
    11: 'br_green',
    12: 'br_cyan',
    13: 'br_red',
    14: 'br_magenta',
    15: 'br_brown',
    16: 'br_white',
}


def transform_movie(mov, appState=None):
    export_movie(mov, appState)
    # return mov, unmodified
    return mov

def export_movie(mov, appState=None):
    # Loads a .COM code file (IBM-PC), appends data to the end.
    # 2 bytes: 16 bit unsigned int, little endian
    # containing the size of the art data below (in bytes)
    # XX bytes, in pairs: ASCII character byte (CP437),
    # attribute byte (FG, BG, Intensity, Underline).
    # .COM file compiled with TASM 4.
    # This pathlib Path is relative to the location of this .py file:
    com_file_directory = pathlib.Path(__file__).parent.joinpath("../msdos/")
    com_file_path = f"{com_file_directory}/dur-com-code-only.bin"
    with open(com_file_path, 'rb') as f:
        com_header_data = f.read()

    width = 80
    height = 25

    # 4000 bytes (B800h format)
    new_num_bytes = width * height * 2  # char + attribyte
    # H is 16-bit unsigned integer (8086 word), < is little endian
    new_num_bytes_bytes = struct.pack('<H', new_num_bytes)

    new_bytes = com_header_data + new_num_bytes_bytes

    for lineNum in range(height):
        for colNum in range(width):
            # convert char to cp437
            try:
                newChar = mov.currentFrame.content[lineNum][colNum].encode('cp437')
            except IndexError:
                # file is smaller than 80x25. Just roll with it
                newChar = ' '.encode('cp437')
            except UnicodeEncodeError:
                # not a cp437 compatible character, default blank
                newChar = ' '.encode('cp437')

            # get colors
            try:
                fgColorNum = mov.currentFrame.newColorMap[lineNum][colNum][0]
            except IndexError:
                fgColorNum = 8    # default white
            try:
                bgColorNum = mov.currentFrame.newColorMap[lineNum][colNum][1] + 1
            except IndexError:
                bgColorNum = 1    # default black
            if appState.colorMode == '256':
                fgColorNum += 1
                bgColorNum = 0
            # no 256 color support for CGA/VGA textmode.
            if fgColorNum > 16:
                fgColorNum = 8    # default white
            if bgColorNum > 8:
                bgColorNum = 0
            colorName = durdraw_colors_16[fgColorNum]
            fgColorValue = cga_fg_colors[colorName]

            colorName = durdraw_colors_16[bgColorNum]
            bgColorValue = cga_bg_colors[colorName]

            # composite FG and BG bits (Bitwise OR)
            colorValue = fgColorValue | bgColorValue

            # make raw bytes, add them
            packedChar = struct.pack('<c', newChar)
            packedColor = struct.pack('<B', colorValue)
            new_bytes = (new_bytes + packedChar + packedColor)
    # file to write
    with open(opts["file name"], 'wb') as f:
        f.write(new_bytes)

    # True on success, False on fail
    return True
 


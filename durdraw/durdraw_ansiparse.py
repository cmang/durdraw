#!/usr/bin/env python3 

# Theory of operation notes:
# A code starts with '\x1B[' or ^[ and ends with a LETTER.
# The ltter is usually 'm' (for Select Graphic Rendition).
# Note that it may end with a letter other than 'm' for some features,
# like cursor movements. For example:
# ^[3A means "move cursor up 3 lines"
# A code looks like this: ^[1;32m for bold color 32. ^[0m for reset.
# ^[0;4;3;42m for reset (0), underline (4), italic (3), background color (42).
# We have a state machine that has attributes. Color, bold, underline, italic, etc.
#
# References:
# Escape code bible: https://en.wikipedia.org/wiki/ANSI_escape_code
# ANSI Sauce (metadata) spec: https://www.acid.org/info/sauce/sauce.htm


import sys
import struct
from itertools import count
import pdb
import durdraw.durdraw_movie as durmovie
import durdraw.durdraw_color_curses as dur_ansilib
import durdraw.durdraw_sauce as dursauce
import durdraw.plugins.convert_charset as durchar
import durdraw.log as log

LOGGER = log.getLogger('ansiparse', level='DEBUG', override=True)

def ansi_color_to_durcolor(ansiColor):
    colorName = ansi_color_to_durcolor_table[ansiColor]
    durColor = color_name_to_durcolor_table[colorName]
    return durColor

ansi_color_to_durcolor_table = {
    # foreground
    '30': 'Black',
    '31': 'Red',
    '32': 'Green',
    '33': 'Yellow',
    '34': 'Blue',
    '35': 'Magenta',
    '36': 'Cyan',
    '37': 'White',
    # background
    '40': 'Black',
    '41': 'Red',
    '42': 'Green',
    '43': 'Yellow',
    '44': 'Blue',
    '45': 'Magenta',
    '46': 'Cyan',
    '47': 'White'
}

color_name_to_durcolor_table = {
    'Black': 0,
    'Red': 5,
    'Green': 3,
    'Yellow': 7,
    'Blue': 2,
    'Magenta': 6,
    'Cyan': 4,
    'White': 8,
    
    'Black': 00,
    'Red': 00,
    'Green': 00,
    'Yellow': 00,
    'Blue': 00,
    'Magenta': 00,
    'Cyan': 00,
    'White': 00
}

def find_next_alpha(text, i):
    for j in count(i):
        if text[j].isalpha():
            return j
    return None


def get_width_and_height_of_ansi_blob(text, width=80):
    i = 0   # index into the file blob
    col_num = 0
    line_num = 0
    max_col = 0
    while i < len(text):
        if i % 10_000 == 0:
            LOGGER.debug('scanning', {'i': i, 'total': len(text), 'pct': round(i / len(text) * 100, 2)})
        # If there's an escape code, extract data from it
        if text[i:i + 2] == '\x1B[':    # Match ^[
            match = find_next_alpha(text, i+1)
            if not match:
                i += 1 # move on to next byte
                continue
            end_index = match   # where the code ends
            if text[end_index] == 'A':      # Move the cursor up X spaces
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = 1
                move_by_amount = int(escape_sequence)
                line_num = line_num - move_by_amount
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'B':      # Move the cursor down X spaces
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = 1
                move_by_amount = int(escape_sequence)
                line_num += move_by_amount
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'C':      # Move the cursor forward X spaces
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = 1
                move_by_amount = int(escape_sequence)
                col_num += move_by_amount
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'D':      # Move the cursor back X spaces
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = 1
                move_by_amount = int(escape_sequence)
                col_num = col_num - move_by_amount
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'H':      # Move the cursor to row/column
                escape_sequence = text[i + 2:end_index]
                escape_codes = escape_sequence.split(';')
                if len(escape_codes) > 1:   # row ; column
                    if escape_codes[0].isnumeric():
                        line_num = int(escape_codes[0])
                    if escape_codes[1].isnumeric():
                        col_num = int(escape_codes[1])
                elif len(escape_codes) == 1:   # row, column=1
                    #line_num = 1
                    if escape_codes[0].isnumeric():
                        col_num = int(escape_codes[0])
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'J':      # Clear screen
                # 0 or none = clear from cursor to end of screen
                # 1 = from cursor to top of screen
                # 2 = clear screen and move cursor to top left
                # 3 = clear entire screen and delete all lines saved in the scrollback buffer
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = '0'   # default - clear from cursor to end
                if escape_sequence == '2':  # cls, move to top left
                    # using a sledgehammer to claer the screen
                    #new_frame = durmovie.Frame(width, height + 1)
                    col_num, line_num = 0, 0
                i = end_index + 1   # move on to next byte
                continue
            elif text[end_index] == 's':    # save current position/state
                saved_col_num = col_num
                saved_line_num = line_num
            elif text[end_index] == 'u':    # restore saved position/state
                col_num = saved_col_num
                line_num = saved_line_num
            i = end_index + 1
            continue    # jump the while
        # Or, not an escape character
        elif text[i] == '\n':   # new line (LF)
            line_num += 1
            if col_num > max_col:
                max_col = col_num
            col_num = 0
        elif text[i] == '\r':  # windows style newline (CR)
            pass    # pfft
        elif text[i:i + 5] == 'SAUCE' and len(text) - i == 128:   # SAUCE record found
            i += 128
            # Wee, I'm flying
        else:   # printable character (hopefully)
            if col_num == width:
                col_num = 0
                line_num += 1
            character = text[i]
            character = text[i]
            col_num += 1
        i += 1
    #print("")
    width = max_col
    height = line_num
    return width, height

def parse_ansi_escape_codes(text, filename = None, appState=None, caller=None, console=False, debug=False, convert_control_codes=True, maxWidth=80):
    """ Take an ANSI file blob, load it into a DUR frame object, return 
        frame """
    sauce = None

    if type(text) is bytes:
        text = text.decode('cp437')
    if filename:
        # If we can just pull it from the Sauce, cool
        sauce = dursauce.SauceParser()
        sauce.parse_file(filename)
        if sauce.sauce_found:
            appState.sauce = sauce
            #if sauce.height > 0 and sauce.width > 0:
            #if sauce.height == None:
            #    sauce.height = 25
            if sauce.width == None:
                #sauce.width = 80
                sauce.width = maxWidth
            maxWidth = sauce.width
            width = sauce.width
            height = sauce.height
            #caller.notify(f"Sauce pulled: author: {sauce.author}, title: {sauce.title}, width {width}, height {height}")
    if sauce != None:
        if not sauce.height:
            width, height = get_width_and_height_of_ansi_blob(text)
            width = sauce.width
        if not sauce.sauce_found or width > 200 or height > 1200:   # let the dodgy function guess
            width, height = get_width_and_height_of_ansi_blob(text)
    else:
        width, height = get_width_and_height_of_ansi_blob(text)

    width = max(width, maxWidth)
    #width = max(width, 80)
    height += 1
    #if appState.debug:
    #    caller.notify(f"Guessed width: {width}, height: {height}")
    #width = min(width, maxWidth)
    height = max(height, 25)

    if appState.wrapWidth == 80 and width > 750:
        # I think something is probably wrong. Bad width and/or height.
        # But, allow --wrap to override this check.
        width = 80
    if height > 8500:
        height = 1000
        #print(f"Bad height or width. Width: {width}, height: {height}")
        #pdb.set_trace()
    new_frame = durmovie.Frame(width, height + 1)
    #if appState.debug:
    #    caller.notify(f"debug: maxWidth = {maxWidth}")
    #parsed_text = ''
    #color_codes = ''
    i = 0   # index into the file blob
    col_num = 0
    line_num = 0
    max_col = 0
    default_fg_color = appState.defaultFgColor
    default_bg_color = appState.defaultBgColor
    fg_color = default_fg_color
    bg_color = default_bg_color
    bold = False
    saved_col_num = 0
    saved_line_num = 0
    saved_byte_location = 0
    parse_error = False
    while i < len(text):
        if i % 10_000 == 0:
            LOGGER.debug('parsing', {'i': i, 'total': len(text), 'pct': round(i / len(text) * 100, 2)})
        # If there's an escape code, extract data from it
        if text[i:i + 2] == '\x1B[':    # Match ^[[
            match = find_next_alpha(text, i+1)
            if not match:
                i += 1 # move on to next byte
                continue
            end_index = match   # where the code ends
            if text[end_index] == 'm':      # Color/SGR control code
                escape_sequence = text[i + 2:end_index]
                escape_codes = escape_sequence.split(';')
                codeList = []
                for code in escape_codes:
                    try:
                        codeList.append(int(code))
                    except:
                        if caller:
                            pass
                            #caller.notify(f"Error in byte {i}, char: {code}, line: {line_num}, col: {col_num}")
                if len(codeList) > 1 and appState.colorMode == "256":
                    # 256 foreground color
                    bg_color = default_bg_color
                    if codeList[0] == 38 and codeList[1] == 5 and len(codeList) == 3:
                        fg_color = codeList.pop()
                        codeList = [fg_color]
                    # 256 background color
                    elif codeList[0] == 48 and codeList[1] == 5 and len(codeList) == 3:
                        bg_color = codeList.pop()
                        codeList = [fg_color]
                # Not a 256 color code - treat as 16 color
                for code in codeList:
                    if code == 0:   # reset
                        fg_color = default_fg_color
                        bg_color = default_bg_color
                        bold = False
                    if code == 1:   # bold
                        bold = True
                    # In case we're still using a previous color with new attributes
                    if fg_color < 9:  # sledgehammer
                        if bold:
                            fg_color += 8
                    # 16 Colors
                    if code > 29 and code < 38: # FG colors 0-8, or 30-37
                        if bold:
                            code += 60  # 30 -> 90, etc, for DOS-style bright colors that use bold
                            #bold = False
                        if appState.colorMode == "256":
                            fg_color = dur_ansilib.ansi_code_to_dur_16_color[str(code)] 
                        else:
                            #if bold:
                            #    code += 60  # 30 -> 90, etc, for DOS-style bright colors that use bold
                            fg_color = dur_ansilib.ansi_code_to_dur_16_color[str(code)] 
                            #if bold:
                            #    fg_color += 8
                        # fix for durdraw color pair stupidity
                        if fg_color == -1 or fg_color == 0: # black fg and bright black fg fix
                            if bold:
                                fg_color = 9
                            else:
                                fg_color = 1
                        #if fg_color == 8:   # bright white fix
                        #    if bold:
                        #        fg_color = 16
                        #bold = False
                        if fg_color < 9:  # sledgehammer
                            if bold:
                                fg_color += 8
                    elif code > 39 and code < 48: # BG colors 0-8, or 40-47
                        if appState.colorMode == "256":
                            #bg_color = dur_ansilib.ansi_code_to_dur_16_color[str(code)] - 1
                            #bg_color = 0
                            bg_color = dur_ansilib.ansi_code_to_dur_16_color[str(code)] - 1
                            if bg_color == -1:
                                bg_color = 0
                        else:
                            #if bold:
                            #    code += 60  # 30 -> 90, etc, for DOS-style bright colors that use bold
                            bg_color = dur_ansilib.ansi_code_to_dur_16_color[str(code)] - 1
                            if bg_color == -1:
                                bg_color = 0
                    if fg_color == -1 or fg_color == 0: # black fg and bright black fg fix
                        if bold:
                            fg_color = 9
                        else:
                            fg_color = 1
                    # 256 Colors
                #if console:    
                #    print(str(escape_codes), end="")

                # Add color to color map
                try:
                    new_frame.newColorMap[line_num][col_num] = [fg_color, bg_color]
                except Exception as E:
                    if console:    
                        print(str(E))
                        print(f"line num: {line_num}")
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'A':      # Move the cursor up X spaces
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = 1
                move_by_amount = int(escape_sequence)
                line_num = line_num - move_by_amount
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'B':      # Move the cursor down X spaces
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = 1
                move_by_amount = int(escape_sequence)
                line_num += move_by_amount
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'C':      # Move the cursor forward X spaces
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = 1
                move_by_amount = int(escape_sequence)
                if col_num >= maxWidth:
                    col_num = 0
                    line_num += 1
                col_num += move_by_amount
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'D':      # Move the cursor back X spaces
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = 1
                move_by_amount = int(escape_sequence)
                col_num = col_num - move_by_amount
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'H':      # Move the cursor to row/column
                escape_sequence = text[i + 2:end_index]
                escape_codes = escape_sequence.split(';')
                if len(escape_codes) > 1:   # row ; column
                    if escape_codes[0].isnumeric():
                        line_num = int(escape_codes[0])
                    if escape_codes[1].isnumeric():
                        col_num = int(escape_codes[1])
                elif len(escape_codes) == 1:   # row, column=1
                    #line_num = 1
                    if escape_codes[0].isnumeric():
                        col_num = int(escape_codes[0])
                i = end_index + 1
                continue    # jump the while
            elif text[end_index] == 'J':      # Clear screen
                # 0 or none = clear from cursor to end of screen
                # 1 = from cursor to top of screen
                # 2 = clear screen and move cursor to top left
                # 3 = clear entire screen and delete all lines saved in the scrollback buffer
                escape_sequence = text[i + 2:end_index]
                if len(escape_sequence) == 0:
                    escape_sequence = '0'   # default - clear from cursor to end
                if escape_sequence == '2':  # cls, move to top left
                    # using a sledgehammer to claer the screen
                    new_frame = durmovie.Frame(width, height + 1)
                    col_num, line_num = 0, 0
                i = end_index + 1   # move on to next byte
                continue
            elif text[end_index] == 's':    # save current position/state
                #saved_col_num = col_num
                #saved_line_num = line_num
                i = end_index + 1   # move on to next byte
                #saved_byte_location = i
                continue
            elif text[end_index] == 'u':    # restore saved position/state
                #col_num = saved_col_num
                #line_num = saved_line_num
                #i = saved_byte_location
                i = end_index + 1   # move on to next byte
                #pdb.set_trace()
                continue
            else:   # Some other escape code, who cares for now
                if appState.debug:
                    caller.notify(f"Unknown escape character type encountered: {text[end_index]}")
                i = end_index + 1   # move on to next byte
                continue
        # Or, not an escape character
        elif text[i] == '\n':   # new line (LF)
            line_num += 1
            if col_num > max_col:
                max_col = col_num
            col_num = 0
        elif text[i] == '\r':  # windows style newline (CR)
            pass    # pfft
        elif text[i] == '\x00': # Null byte
            pass
        elif text[i] == '\x1a': # ctl-z code, EOF, just before the SAUCE
            pass
        #elif text[i] == '\x01': # CTRL-A, SOH (start header).
        #    # Q: Why is this in some ANSIs? A: Because it's a smiley face in CP437
        #    pass
        #elif text[i] == '\x02': # CTRL-B, STX (start text)
        #    pass
        elif text[i:i + 5] == 'SAUCE' and len(text) - i == 128:   # SAUCE record found
            i += 128
        else:   # printable character (hopefully)
            if col_num >= maxWidth:
                col_num = 0
                line_num += 1
            character = text[i]
            try:
                # Convert CP437 control codes
                if ord(character) < 0x19:
                    character = chr(durchar.cp437_control_codes_to_utf8[ord(character)])
                new_frame.content[line_num][col_num] = character
            except TypeError as E:
                print(f"Type error, likely on text: {E}")
                pdb.set_trace()
            except IndexError:
                parse_error = True
                if debug:
                    caller.notify(f"Error writing content. Width: {width}, Height: {height}, line: {line_num}, col: {col_num}, char: {character}, pos: {i}")
            try:
                new_frame.newColorMap[line_num][col_num] = [fg_color, bg_color]
            except IndexError:
                parse_error = True
                if debug:
                    caller.notify(f"Error writing color. Width: {width}, Height: {height}, line: {line_num}, col: {col_num}, pos: {i}")
           # if console:    
           #     print(character, end='')
            col_num += 1
        i += 1
    if console:    
        print("")
        print(f"Lines: {line_num}, Columns: {max_col}")
    if parse_error and appState.debug:
        caller.notify(f"Possible errors detected while loading this file. It may not display correctly.")
    height = line_num
    width = max_col
    frame = durmovie.Frame(height, width)
    line_num = 0
    col_num = 0
    # maybe usethis for the color: dur_ansilib.ansi_code_to_dur_16_color[fg_ansi]
    return new_frame


if __name__ == "__main__":
    # Example usage
    #file_path = 'kali.ans'
    #file_path = '11.ANS'
    file_path = '../rainbow.ans'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    with open(file_path, 'r') as file:
        try:
            text_with_escape_codes = file.read()
        except UnicodeDecodeError:
            file.close()
            file = open(file_path, "r", encoding="cp437")
            #file = open(file_path, "r", encoding="big5")
            text_with_escape_codes = file.read()
        #parsed_text, fg, bg = parse_ansi_escape_codes(text_with_escape_codes)
        newFrame = parse_ansi_escape_codes(text_with_escape_codes,  console=True)
        print(str(newFrame.newColorMap))
        print(str(newFrame.content))
        print(str(newFrame))
        #print(parsed_text)
        #print(f"Fg: {fg}, bg: {bg}")



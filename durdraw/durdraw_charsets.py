# Load character sets from files, initialize them 
# <block first-cp="1FB00" last-cp="1FBFF" name="Symbols for Legacy Computing"/>
# We can return a charMap that looks like this: [ {'f1':\x1FB00, 
# 895         self.fullCharMap = [ \
# 896             # All of our unicode templates live here. Blank template:
# 897             #{'f1':, 'f2':, 'f3':, 'f4':, 'f5':, 'f6':, 'f7':, 'f8':, 'f9':, 'f10':},
# 898
# 899             # block characters
# 900             {'f1':9617, 'f2':9618, 'f3':9619, 'f4':9608, 'f5':9600, 'f6':9604, 'f7':9612, 'f8':9616, 'f9':     9632, 'f10':183 },    # ibm-pc looking block characters (but unicode instead of ascii)

import pdb

import pathlib
import xml.etree.ElementTree as ET

def hex_range_iterator(start_hex, end_hex):
    """ Iterator that takes a first and last hex number, and returns each one
        in succession.
        Used to generate character sets from unicode-provided ranges
        # Example usage:
        start_hex = "1FB00"
        end_hex = "1FBFF"
        for hex_value in hex_range_iterator(start_hex, end_hex):
            print(hex_value)
    """
    start_int = int(start_hex, 16)  # Convert start_hex to an integer
    end_int = int(end_hex, 16)      # Convert end_hex to an integer
    current_int = start_int
    while current_int <= end_int:
        #yield format(current_int, 'X')  # Convert the integer back to hexadecimal
        #yield hex(current_int)
        yield current_int
        current_int += 1

def parse_xml_blocks_file(xml_file_path):
    """ laod XML file, returns block_data object, containing all the block
        names and their first and last code point (hex value)
     """
    block_data = {}

    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Iterate through the 'block' elements and extract the data
    for block_element in root.findall('.//block'):
        first_cp = block_element.get('first-cp')
        last_cp = block_element.get('last-cp')
        block_name = block_element.get('name')
        
        if block_name is not None and first_cp is not None and last_cp is not None:
            block_data[block_name] = {
                'first-cp': first_cp,
                'last-cp': last_cp
            }
    return block_data

# We can return a fullCharMap that looks like this: [ {'f1':\x1FB00, 
# 895         self.fullCharMap = [ \
# 896             # All of our unicode templates live here. Blank template:
# 897             #{'f1':, 'f2':, 'f3':, 'f4':, 'f5':, 'f6':, 'f7':, 'f8':, 'f9':, 'f10':},
# 898
# 899             # block characters
# 900             {'f1':9617, 'f2':9618, 'f3':9619, 'f4':9608, 'f5':9600, 'f6':9604, 'f7':9612, 'f8':9616, 'f9':     9632, 'f10':183 },    # ibm-pc looking block characters (but unicode instead of ascii)

def load_unicode_block(block_name: str):
    """ returns a fullCharMap """
    #xml_block_filename = 'unicode-groups.xml'
    xml_block_filename = pathlib.Path(__file__).parent.joinpath("charsets/unicode-groups.xml")
    block_data = parse_xml_blocks_file(xml_block_filename)
    if block_name in block_data:
        block_info = block_data[block_name]
        #print(f"Block: {block_name}")
        #print(f"First Code Point: {block_info['first-cp']}")
        #print(f"Last Code Point: {block_info['last-cp']}")
        first_cp = block_info['first-cp']
        last_cp = block_info['last-cp']
        charMap = []
        fKeyList = {'f1':'', 'f2':'', 'f3':'', 'f4':'', 'f5':'', 'f6':'', 'f7':'', 'f8':'', 'f9':'', 'f10':''}
        fKeyNum = 1
        # go through each code point, assign them to F1-F10, and add those f1-f10
        # sets to the larger full character map
        for code_point in hex_range_iterator(first_cp, last_cp):
            #fKeyList[f'f{fKeyNum}'] = chr(code_point)
            #fKeyList[f'f{fKeyNum}'] = f'\U{hex(code_point)}'
            fKeyList[f'f{fKeyNum}'] = code_point
            if fKeyNum == 10:
                charMap.append(fKeyList.copy())
                fKeyNum = 1
            else:
                fKeyNum += 1
            #print(str(fKeyList))
        return charMap
    else:
        #print(f"Block '{block_name}' not found in the XML data.")
        # this should not happen, so...
        return None

def get_unicode_blocks_list():
    xml_block_filename = pathlib.Path(__file__).parent.joinpath("charsets/unicode-groups.xml")
    block_data = parse_xml_blocks_file(xml_block_filename)
    block_list = list(block_data.keys())
    block_list = block_list[1:] # cut off Basic Latin, or 0000-007F, as 0000 is a null character
    return block_list

if __name__ == "__main__":
    #charMap = load_unicode_block("Chess Symbols")
    #charMap = load_unicode_block("Symbols for Legacy Computing")
    #charMap = load_unicode_block("Emoticons")
    #print(str(charMap))
    unicodeBlocksList = get_unicode_blocks_list()
    print(str(unicodeBlocksList))

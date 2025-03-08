# Run Neofetch. Extract data from it. Return a dict containing neofetch data.

import os
import pathlib
import re
import subprocess

neo_keys = ['OS', 'Host', 'Kernel', 'Uptime', 'Packages', 'Shell', 'Resolution', 'DE', 'WM', 'WM Theme', 'Terminal', 'Terminal Font', 'CPU', 'GPU', 'Memory']

def strip_escape_codes(text):
    # 7-bit C1 ANSI sequences
    ansi_escape = re.compile(r'''
        \x1B  # ESC
        (?:   # 7-bit C1 Fe (except CSI)
            [@-Z\\-_]
        |     # or [ for CSI, followed by a control sequence
            \[
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        )
    ''', re.VERBOSE)
    text = ansi_escape.sub('', text)
    text = re.sub(r'\d+\.\d+ms', '', text).strip()
    return text

def fetcher_available(name="neofetch"):
    arg = "--version"
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name, arg], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        #if e.errno == os.errno.ENOENT:
        #    return False
        return False
    return True

def run():
    # make an empty dict of Neofetch keys for us to populate and return
    neofetch_results = {}
    for key in neo_keys:
        neofetch_results[key] = ''
    # Run neofetch, capture the output
    #fetcher_exec = pathlib.Path(__file__).parent.joinpath("neofetch/neofetch")
    fetcher_exec = ["neofetch", "--stdout"]  # not a full path. just the executable run from the $PATH
    #fetcher_exec = ["fastfetch", "-c", "ci"]  # not a full path. just the executable run from the $PATH
    neofetch_output = subprocess.check_output(fetcher_exec).decode()
    neofetch_lines = neofetch_output.split('\n')[2:]
    # Parse the neofetch output into neofetch_results{}
    for line in neofetch_lines:
        if line == '':
            break
        try:
            line = strip_escape_codes(line)
            key = line.split(': ')[0].strip()
            value = line.split(': ')[1].strip()
            #value = value.split('    ')[0].strip()
            # Remove trailing "          0.020ms" crap.
            #new_value = re.sub(r'ms$', " ", value)
            #new_value = re.sub(r'\s+\d+\.\d+ms$', '', value).strip()
            new_value = value
            #print(f"found key: {key}, new_value: {new_value}")
        except:
            break
        if key in neo_keys:
            neofetch_results[key] = value
    return neofetch_results

if __name__ == "__main__":
    results = run()
    print(results)

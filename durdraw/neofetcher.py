# Run Neofetch. Extract data from it. Return a dict containing neofetch data.

import os
import shutil
import re
import subprocess
from typing import OrderedDict

neo_keys = ['OS', 'Host', 'Kernel', 'Uptime', 'Packages', 'Shell', 'Resolution', 'DE', 'WM', 'WM Theme', 'Terminal', 'Terminal Font', 'CPU', 'GPU', 'Memory']

# list of available fetchers - name: cmd
# dictionary order determines cmd priority if multiple are present
od_fetchers = OrderedDict({
    "fastfetch": ["fastfetch", "--pipe", "-l", "none"],
    "neofetch": ["neofetch", "--stdout", "--config", "none"],
})

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

def fetcher_available(name: str) -> bool:
    return (name in od_fetchers) and bool(shutil.which(name))

def find_available_fetcher() -> str:
    for key, _ in od_fetchers.items():
        if fetcher_available(key):
            return key
    return ""

def run(fetcher=""):
    if not fetcher and not (fetcher := find_available_fetcher()):
         return

    # make an empty dict of Neofetch keys for us to populate and return
    fetch_results = {key: '' for key in neo_keys}
    # ignore parent process so fastfetch correctly determines the shell
    env = os.environ.copy()
    env['FFTS_IGNORE_PARENT'] = '1'
    fetch_output = subprocess.check_output(od_fetchers[fetcher], env=env).decode(errors='replace')
    fetch_lines = fetch_output.split('\n')[2:]
    # Parse the fetch output into fetch_results{}
    for line in fetch_lines:
        if line == '':
            break
        try:
            #line = strip_escape_codes(line)
            key = line.split(': ')[0].strip()
            value = line.split(': ')[1].strip()
            #value = value.split('    ')[0].strip()
            # Remove trailing "          0.020ms" crap.
            #new_value = re.sub(r'ms$', " ", value)
            #new_value = re.sub(r'\s+\d+\.\d+ms$', '', value).strip()
            #new_value = value
            #print(f"found key: {key}, new_value: {new_value}")
        except:
            break
        if key in fetch_results:
            fetch_results[key] = value
    return fetch_results

if __name__ == "__main__":
    results = run()
    print(results)

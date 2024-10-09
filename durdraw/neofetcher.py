# Run Neofetch. Extract data from it. Return a dict containing neofetch data.

import pathlib
import subprocess

neo_keys = ['OS', 'Host', 'Kernel', 'Uptime', 'Packages', 'Shell', 'Resolution', 'DE', 'WM', 'WM Theme', 'Terminal', 'Terminal Font', 'CPU', 'GPU', 'Memory']



def isAppAvail(name):   # looks for program 'name' in path
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        #if e.errno == os.errno.ENOENT:
        #    return False
        return False
    return True

def fetcher_available_old():    # old because it looks internally the local path instead of global path
    """ Returne True if Neofetch was able to run successfully. """
    try:
        neofetch_path = pathlib.Path(__file__).parent.joinpath("neofetch/neofetch")
        subprocess.run([neofetch_path, '--stdout'])
        return True
    except:
        return False

def fetcher_available():
    return isAppAvail("neofetch")

def run():
    # make an empty dict of Neofetch keys for us to populate and return
    neofetch_results = {}
    for key in neo_keys:
        neofetch_results[key] = ''
    # Run neofetch, capture the output
    #neofetch_path = pathlib.Path(__file__).parent.joinpath("neofetch/neofetch")
    neofetch_path = "neofetch"  # obviously not a full path. just the executable run from the $PATH
    neofetch_output = subprocess.check_output([neofetch_path, '--stdout']).decode()
    neofetch_lines = neofetch_output.split('\n')[2:]
    # Parse the neofetch output into neofetch_results{}
    for line in neofetch_lines:
        if line == '':
            break
        try:
            key = line.split(': ')[0].strip()
            value = line.split(': ')[1].strip()
        except:
            break
        if key in neo_keys:
            neofetch_results[key] = value
    return neofetch_results

if __name__ == "__main__":
    results = run()
    print(results)

# Run Neofetch. Extract data from it. Return a dict containing neofetch data.

import pathlib
import subprocess

neo_keys = ['OS', 'Host', 'Kernel', 'Uptime', 'Packages', 'Shell', 'Resolution', 'DE', 'WM', 'WM Theme', 'Terminal', 'Terminal Font', 'CPU', 'GPU', 'Memory']

def fetcher_available():
    """ Returne True if Neofetch was able to run successfully. """
    try:
        neofetch_path = pathlib.Path(__file__).parent.joinpath("neofetch/neofetch")
        subprocess.run([neofetch_path, '--stdout'])
        return True
    except:
        return False

def run():
    # make an empty dict of Neofetch keys for us to populate and return
    neofetch_results = {}
    for key in neo_keys:
        neofetch_results[key] = ''
    # Run neofetch, capture the output
    neofetch_path = pathlib.Path(__file__).parent.joinpath("neofetch/neofetch")
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

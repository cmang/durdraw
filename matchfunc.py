#!/usr/bin/env python3
'''
usage ./matchfunc.py PATTERN OFNAME
e.g. ./matchfunc.py 'push()' push.json
'''

import json
import os
import sys

def matchInFile(pattern, filepath):
    matches = []

    lines = list(map(str.strip, open(filepath).readlines()))

    for i, l in enumerate(lines):
        if pattern in l:
            for j in range(i, 0, -1):
                if 'def ' in lines[j]:
                    matches.append({'func': {'idx': j, 'line': lines[j]}, 'match': {'idx': i, 'line': l}})
                    break
    return matches


def matchInRepo(dirname, pattern):
    matches = {}
    for dirpath, _, filenames in os.walk(dirname):
        for f in filenames:
            if not f.endswith('.py'):
                continue
            path = os.path.join(dirpath, f)
            fileMatches = matchInFile(pattern, path)
            if fileMatches:
                matches[path] = fileMatches
    return matches

pattern, ofname = sys.argv[1:]

matches = matchInRepo('durdraw', pattern)

with open(ofname, 'w') as ostream:
    for f, ms in matches.items():
        for m in ms:
            print(json.dumps({'file': f, 'matches': m}), file=ostream)


#!/usr/bin/env python3

import json
import os

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
    for dirpath, dirnames, filenames in os.walk(dirname):
        for f in filenames:
            if not f.endswith('.py'):
                continue
            path = os.path.join(dirpath, f)
            fileMatches = matchInFile(pattern, path)
            if fileMatches:
                matches[path] = fileMatches
    return matches

matches = matchInRepo('durdraw', 'push()')

with open('matches.json', 'w') as ostream:
    for f, ms in matches.items():
        for m in ms:
            print(json.dumps({'file': f, 'matches': m}), file=ostream)


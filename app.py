#!/usr/bin/env python -m
import json

import yaml

import src.isparser
from src.savelib import save_tsv

files = [
    'textreference/02-cantrips.txt',
    'textreference/03-monographs.txt',
    'textreference/04-incantations.txt',
    'textreference/05-objects-of-power.txt',
    'textreference/06-spells.txt',
    'textreference/07-epherma.txt',
    'textreference/10-forte.txt',
    'textreference/18-character-secrets.txt',
    'textreference/19-house-secrets.txt'
]

if __name__ == "__main__":
    data = src.isparser.parse_all(files)
    open('output/all-data.json', 'w').write(json.dumps(data))
    open('output/all-data.yaml', 'w').write(yaml.dump(data))

    for filetype in data.keys():
        filename = filetype.lower().replace(' ', '-')
        save_tsv(data[filetype], "output/%s.tsv" % filename)
        open('output/%s.json' % filename, 'w').write(json.dumps(data[filetype]))
        open('output/%s.yaml' % filename, 'w').write(yaml.dump(data[filetype]))

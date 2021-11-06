#!/usr/bin/env python -m
import json
import yaml
from src.savelib import save_tsv
import src.isparser

sources = [
    {
        "filebase": '02-cantrips',
        "type": 'cantrips'
    },
    {
        "filebase": '04-incantations',
        "type": 'incantations'
    },
    {
        "filebase": '05-objects-of-power',
        "type": 'objects-of-power'
    },
    {
        "filebase": '06-spells',
        "type": 'spells'
    },
    {
        "filebase": '07-epherma',
        "type": 'epherma'
    }
]

if __name__ == "__main__":
    for src in sources:
        data = src.isparser.parse("textreference/%s.txt" % src['filebase'], src['type'])
        save_tsv(data, "output/tsv/%s.tsv" % src['filebase'])
        open('output/json/%s.json' % src['filebase'], 'w').write(json.dumps(data))
        open('output/yaml/%s.yaml' % src['filebase'], 'w').write(yaml.dump(data))

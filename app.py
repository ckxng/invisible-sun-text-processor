#!/usr/bin/env python
import re
import json
import yaml


def save_tsv(data, filename):
    """
    Saves a data dict as a file in Tab Separated Value form.

    Where data follows the form:
    {
      {
        key: value1a
        key2: value1b
        key3: value1c
      },
      {
        key: value2a
        key2: value2b
        key3: value2c
      },
    }

    The output will be:
    key1\tkey2\tkey3
    value1a\tvalue1b\tvalue1c
    value2a\tvalue2b\tvalue2c

    :param dict data: a dict of dict of data to write
    :param str filename: the filename to write to
    """
    f = open(filename, 'w')
    data_keys = {}
    for k in data.keys():
        for kk in data[k]:
            data_keys[kk] = 1
    ordered_keys = data_keys.keys()

    f.write("\t".join(ordered_keys) + "\n")

    for k in data.keys():
        vals = []
        for ok in ordered_keys:
            if ok in data[k].keys():
                vals.append(data[k][ok])
            else:
                vals.append('')
        f.write("\t".join(vals) + "\n")
    f.close()


def parse_02_cantrips(filename):
    """
    Parse the cantrips text file provided by MCG
    :param str filename: the filename of the text file
    :return: dict of dicts containing parsed data
    """
    re_cantrip = re.compile('^(?P<title>.+) \\((?P<type>[A-Z]+)\\): (?P<form>.+)$')

    data = {}

    for line in open(filename, "r").readlines():
        line = line.rstrip()

        m = re_cantrip.match(line)
        # Found a cantrip
        if m:
            data[m.group('title')] = {
                'Title': m.group('title'),
                'Type': m.group('type'),
                'Form': m.group('form')
            }

    return data



def parse_05_objects_of_power(filename):
    """
    Parse the objects of power text file provided by MCG
    :param str filename: the filename of the text file
    :return: dict of dicts containing parsed data
    """
    found_file_start = 0

    current_title = None
    re_title = re.compile('^(?P<title>.+) \\(OBJECT OF POWER\\)$')

    current_section = None
    re_sections = {
        'Level': re.compile('^Level: (?P<content>.+)$'),
        'Form': re.compile('^Form: (?P<content>.+)$'),
        'Color': re.compile('^Color: (?P<content>.+)$'),
        'Price': re.compile('^(Conventional )?Price:( (?P<content>.+))?'),
        'Effect Depletion': re.compile('^Effect Depletion:( (?P<content>.+))?'),
        'Object Depletion': re.compile('^Object Depletion:( (?P<content>.+))?')
    }
    re_money = re.compile('(gem|orb|bloodsilver)')

    data = {}

    for line in open(filename, "r").readlines():
        line = line.rstrip()

        # Check if this is the correct file, otherwise don't parse
        if line == "OBJECTS OF POWER":
            found_file_start = 1
            current_title = None
            current_section = None
        if not found_file_start:
            continue

        # The current entry is done and we are between entries, stop parsing
        if line == '':
            current_title = None
            current_section = None
            continue

        # If we are between entries
        if not current_title:
            m = re_title.match(line)
            # We found a title, stop parsing
            if m:
                current_title = m.group('title')
                data[current_title] = {
                    'Title': current_title
                }
                continue
            # We have not found a title yet, stop parsing
            else:
                continue

        # This is a special type of item
        if line in ('KINDLED', 'RELIC', 'ARTIFACT'):
            data[current_title]['Type'] = line
            continue

        found_start_of_new_section = 0
        for section in re_sections.keys():
            m = re_sections[section].match(line)
            # We found the beginning of a new section
            if m:
                current_section = section
                data[current_title][current_section] = m.group('content') or ''
                found_start_of_new_section = 1
        # End parsing upon handling the first line of a section
        if found_start_of_new_section:
            # Colors are always single-line, but are sometimes followed by comments
            if current_section == 'Color':
                current_section = 'Comment'
                data[current_title][current_section] = ''
            continue

        # Something is wrong if we are not in the middle of parsing a multiline section, skip
        if not current_section:
            print('Unexpected condition, not in a recognized part of the file')
            continue

        # If we are in the price section and the line does not mention money,
        # then we have actually switched to a comment
        if current_section == 'Price':
            if not re_money.search(line):
                current_section = 'Comment'
                data[current_title][current_section] = ''

        # We are in a multiline section, append the line to the current section
        if data[current_title][current_section] == '':
            data[current_title][current_section] += line
        else:
            data[current_title][current_section] += ' ' + line

    return data

def parse_06_spells(filename):
    """
    Parse the spells text file provided by MCG
    :param str filename: the filename of the text file
    :return: dict of dicts containing parsed data
    """
    found_file_start = 0

    current_title = None
    re_title = re.compile('^(?P<title>.+) \\(SPELL\\)$')

    current_section = None
    re_sections = {
        'Level': re.compile('^Level: (?P<content>.+)$'),
        'Form': re.compile('^Form: (?P<content>.+)$'),
        'Color': re.compile('^Color: (?P<content>.+)$'),
        'Facet': re.compile('^Facets?: (?P<content>.+)$'),
        'Depletion': re.compile('^Depletion: (?P<content>.+)$')
    }

    data = {}

    for line in open(filename, "r").readlines():
        line = line.rstrip()

        # Check if this is the correct file, otherwise don't parse
        if line == "SPELLS":
            found_file_start = 1
            current_title = None
            current_section = None
        if not found_file_start:
            continue

        # The current entry is done and we are between entries, stop parsing
        if line == '':
            current_title = None
            current_section = None
            continue

        # If we are between entries
        if not current_title:
            m = re_title.match(line)
            # We found a title, stop parsing
            if m:
                current_title = m.group('title')
                data[current_title] = {
                    'Title': current_title
                }
                continue
            # We have not found a title yet, stop parsing
            else:
                continue

        found_start_of_new_section = 0
        for section in re_sections.keys():
            m = re_sections[section].match(line)
            # We found the beginning of a new section
            if m:
                current_section = section
                data[current_title][current_section] = m.group('content')
                found_start_of_new_section = 1
        # End parsing upon handling the first line of a section
        if found_start_of_new_section:
            # Levels are always single-line, but are always followed by Effect
            if current_section == 'Level':
                current_section = 'Effect'
                data[current_title][current_section] = ''
            # Colors are always single-line, but are sometimes followed by comments
            elif current_section == 'Color':
                current_section = 'Comment'
                data[current_title][current_section] = ''
            continue

        # Something is wrong if we are not in the middle of parsing a multiline section, skip
        if not current_section:
            print('Unexpected condition, not in a recognized part of the file')
            continue

        # We are in a multiline section, append the line to the current section
        if data[current_title][current_section] == '':
            data[current_title][current_section] += line
        else:
            data[current_title][current_section] += ' ' + line

    return data

def parse_07_ephemera(filename):
    """
    Parse the ephemera text file provided by MCG
    :param str filename: the filename of the text file
    :return: dict of dicts containing parsed data
    """
    found_file_start = 0

    current_title = None
    re_title = re.compile('^(?P<title>.+) \\(EPHEMERA OBJECT\\)$')

    current_section = None
    re_sections = {
        'Level': re.compile('^Level: (?P<content>.+)$'),
        'Form': re.compile('^Form: (?P<content>.+)$'),
        'Color': re.compile('^Color: (?P<content>.+)$'),
        'Depletion': re.compile('^Depletion: (?P<content>.+)$')
    }

    data = {}

    for line in open(filename, "r").readlines():
        line = line.rstrip()

        # Check if this is the correct file, otherwise don't parse
        if line == "EPHEMERA OBJECTS":
            found_file_start = 1
            current_title = None
            current_section = None
        if not found_file_start:
            continue

        # The current entry is done and we are between entries, stop parsing
        if line == '':
            current_title = None
            current_section = None
            continue

        # If we are between entries
        if not current_title:
            m = re_title.match(line)
            # We found a title, stop parsing
            if m:
                current_title = m.group('title')
                data[current_title] = {
                    'Title': current_title
                }
                continue
            # We have not found a title yet, stop parsing
            else:
                continue

        found_start_of_new_section = 0
        for section in re_sections.keys():
            m = re_sections[section].match(line)
            # We found the beginning of a new section
            if m:
                current_section = section
                data[current_title][current_section] = m.group('content')
                found_start_of_new_section = 1
        # End parsing upon handling the first line of a section
        if found_start_of_new_section:
            # Colors are always single-line, but are sometimes followed by comments
            if current_section == 'Color':
                current_section = 'Comment'
                data[current_title][current_section] = ''
            continue

        # Something is wrong if we are not in the middle of parsing a multiline section, skip
        if not current_section:
            print('Unexpected condition, not in a recognized part of the file')
            continue

        # We are in a multiline section, append the line to the current section
        if data[current_title][current_section] == '':
            data[current_title][current_section] += line
        else:
            data[current_title][current_section] += ' ' + line

    return data


if __name__ == "__main__":

    data = parse_02_cantrips("textreference/02-cantrips.txt")
    save_tsv(data, "output/tsv/02-cantrips.tsv")
    open('output/json/02-cantrips.json', 'w').write(json.dumps(data))
    open('output/yaml/02-cantrips.yaml', 'w').write(yaml.dump(data))

    data = parse_05_objects_of_power("textreference/05-objects-of-power.txt")
    save_tsv(data, "output/tsv/05-objects-of-power.tsv")
    open('output/json/05-objects-of-power.json', 'w').write(json.dumps(data))
    open('output/yaml/05-objects-of-power.yaml', 'w').write(yaml.dump(data))

    data = parse_06_spells("textreference/06-spells.txt")
    save_tsv(data, "output/tsv/06-spells.tsv")
    open('output/json/06-spells.json', 'w').write(json.dumps(data))
    open('output/yaml/06-spells.yaml', 'w').write(yaml.dump(data))

    data = parse_07_ephemera("textreference/07-epherma.txt")
    save_tsv(data, "output/tsv/07-ephemera.tsv")
    open('output/json/07-ephemera.json', 'w').write(json.dumps(data))
    open('output/yaml/07-ephemera.yaml', 'w').write(yaml.dump(data))

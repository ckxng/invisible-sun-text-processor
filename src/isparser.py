import re


def parse(filename, type):
    if type == 'cantrips':
        return parse_cantrips(filename)
    elif type == 'epherma':
        return parse_epherma(filename)
    elif type == 'spells':
        return parse_spells(filename)
    elif type == 'incantations':
        return parse_incantations(filename)
    elif type == 'objects-of-power':
        return parse_objects_of_power(filename)
    return None


def parse_cantrips(filename):
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


def parse_incantations(filename):
    """
    Parse the incantations text file provided by MCG
    :param str filename: the filename of the text file
    :return: dict of dicts containing parsed data
    """
    found_file_start = 0

    current_title = None
    re_title = re.compile('^(?P<title>.+) \\(INCANTATION\\)$')

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
        if line == "INCANTATIONS":
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


def parse_objects_of_power(filename):
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

    # Needed for determining the end of a form
    previous_line = None
    re_begins_with_capital = re.compile('^[A-Z]')
    re_ends_with_period = re.compile('\\.$')

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

            # Save this line as the previous line when finding a new section
            previous_line = line
            continue

        # Something is wrong if we are not in the middle of parsing a multiline section, skip
        if not current_section:
            print('Unexpected condition, not in a recognized part of the file')
            continue

        # If we are in the form section and this line begins with a capital letter
        # and the previous line does not end with a period
        # We have moved from form to effect
        if current_section == 'Form' and re_begins_with_capital.match(line) and not re_ends_with_period.search(
                previous_line):
            current_section = 'Effect'
            data[current_title][current_section] = ''

        # If we are in the price section and the line does not mention money,
        # then we have actually switched to a comment
        elif current_section == 'Price':
            if not re_money.search(line):
                current_section = 'Comment'
                data[current_title][current_section] = ''

        # We are in a multiline section, append the line to the current section
        if data[current_title][current_section] == '':
            data[current_title][current_section] += line
        else:
            data[current_title][current_section] += ' ' + line

        # Save this line as the previous line after handling multiline text
        previous_line = line

    return data


def parse_spells(filename):
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


def parse_epherma(filename):
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

    # Needed for determining the end of a form
    previous_line = None
    re_begins_with_capital = re.compile('^[A-Z]')
    re_ends_with_period = re.compile('\\.$')

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

            # Save this line as the previous line when finding a new section
            previous_line = line
            continue

        # Something is wrong if we are not in the middle of parsing a multiline section, skip
        if not current_section:
            print('Unexpected condition, not in a recognized part of the file')
            continue

        # If we are in the form section and this line begins with a capital letter
        # and the previous line does not end with a period
        # We have moved from form to effect
        if current_section == 'Form' and re_begins_with_capital.match(line) and not re_ends_with_period.search(
                previous_line):
            current_section = 'Effect'
            data[current_title][current_section] = ''

        # We are in a multiline section, append the line to the current section
        if data[current_title][current_section] == '':
            data[current_title][current_section] += line
        else:
            data[current_title][current_section] += ' ' + line

        # Save this line as the previous line after handling multiline text
        previous_line = line

    return data

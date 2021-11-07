import re

import deep_merge


def parse_all(filenames):
    """
    Parse any sources from all files specified.
    The source types are automatically detected and returned in a single object
    :param list(str) filenames: the list of filesnames to parse
    :return: dict containing all parsed data
    """

    data = {}

    for filename in filenames:
        deep_merge.merge(data, parse_any(filename))

    return data


def deep_merge_if_found(left, right):
    """
    use deep_merge.merge(left, right) to merge two dicts, but only if right is not empty or None
    WARNING!  The left dict is modified in place.
    :param left: a dictionary that will contain merged content
    :param right: a dictionary that will be merged
    :return: True if a merge took place, otherwise False
    """
    if not right:
        return False
    deep_merge.merge(left, right)
    return True


def check_for_section(line):
    """
    Check this line to see if the current line is the beginning of a new section
    Sometimes a section also contains some content which should be returned as well
    :param line: the line to parse
    :return: a tuple (None or section name, None or content)
    """

    re_sections = {
        'Level': re.compile('^Level: (?P<content>.+)$'),
        'Form': re.compile('^Form: (?P<content>.+)$'),
        'Color': re.compile('^Color: (?P<content>.+)$'),
        'Facet': re.compile('^Facets?: (?P<content>.+)$'),
        'Depletion': re.compile('^Depletion: (?P<content>.+)$'),
        'Price': re.compile('^(Conventional )?Price:( (?P<content>.+))?'),
        'Effect Depletion': re.compile('^Effect Depletion:( (?P<content>.+))?'),
        'Object Depletion': re.compile('^Object Depletion:( (?P<content>.+))?'),
        'Requirements': re.compile('^Requirements:( (?P<content>.+))?')
    }

    for section in re_sections.keys():
        m = re_sections[section].match(line)
        if m:
            if m.group('content'):
                return section, m.group('content')
            else:
                return section, ''

    return None, None


def check_multiline_section_boundary(line, previous_line):
    """
    Return true if line begins with a capital letter and previous_line ends with a period(.)
    :param line: the line to check if it begins with a capital
    :param previous_line: the line to check if it ends with a period
    :return: True if this is a multiline section boundary
    """

    re_begins_with_capital = re.compile('^[A-Z]')
    re_ends_with_period = re.compile('\\.$')

    return re_begins_with_capital.match(line) and not re_ends_with_period.search(previous_line)


def check_money_words(line):
    """
    Return true this line contains words that reference money
    :param line: the line to check
    :return: True if this line references money
    """

    m = re.compile('(gem|orb|bloodsilver)').search(line)
    if m:
        return True
    return False


def check_requirement(line):
    """
    Check this line for a requirement, which is indicated by a line betinning with "?? ".
    If one is found, return that line with a newline at the end, as requirements are always
    a complete line and formatted as a bulleted list.  Replace the "??" with a "-" as well
    so that the resulting list can later be Markdown formatted.
    :param line: the line to check
    :return: None or a formatted requirement
    """
    if line[0:3] == "?? ":
        return "- %s\n" % line[3:]
    return None


def parse_any(filename):
    """
    Parse any sources from the specified file.
    The source type is automatically detected and all sources are returned in a single
    object.
    :param sre filename: a file to parse
    :return: dict containing all parsed data
    """

    data = {
        'Cantrips': {},
        'Ephemera': {},
        'Spells': {},
        'Incantations': {},
        'Objects of Power': {},
        'Monographs': {},
        'Character Secrets': {},
        'House Secrets': {},
        'Forte': {}
    }

    filetype = None
    title = None
    section = None

    # a few file types have a multiline section immediately followed by an effect
    # the only way to detect this section boundary is by comparing the current and previous
    # lines.  (The previous line will have a . and the current line will begin with a capital)
    saved_line = None
    previous_line = None

    for line in open(filename, "r").readlines():
        line = line.rstrip()

        # store the current line so that it can be moved into previous_line next time
        # retrieve the stored line and move it into previous_line
        previous_line = saved_line
        saved_line = line

        # cantrips can be handled on a per-line basis without any additional metadata required
        # stop parsing this line if we found a cantrip
        if deep_merge_if_found(data['Cantrips'], parse_cantrip_line(line)):
            continue

        # if we don't know what kind of file this is yet, search this line for the filetype
        # whether this line contains the filetype or not, move on to the next line after checking
        if not filetype:
            filetype = check_for_filetype(line)
            continue

        # blank lines only appear between entries, so reset the title and section
        # stop parsing this line and check the next one
        if line == '':
            title = None
            section = None
            continue

        # we are between titles, check this line for a title and create an entry for it
        # whether this line contains a title or not, move on to the next entry
        if not title:
            (title, entrytype) = check_for_title(line)
            if title:
                data[filetype][title] = {
                    'Title': title,
                    'Type': entrytype
                }

                # Rarely, an unlabeled comment will immediately follow the title
                section = 'Comment'
                data[filetype][title][section] = ''

            continue

        # Objects of Power have special tags applied to certain items.
        # When this is found, record it and move on to the next entry
        if line in ('KINDLED', 'RELIC', 'ARTIFACT'):
            data[filetype][title]['Type'] = line
            continue

        # we have not yet found a section, all entry types start with a section
        # if a section is found, it may also have content on that same line
        # create the section and save the content
        # additionally, some sections have special rules for parsing
        # after handling all new section logic, stop parsing this line and move on
        (new_section, content) = check_for_section(line)
        if new_section:
            section = new_section
            data[filetype][title][section] = content

            # All filetypes: Level.
            # Levels are always single line and are sometimes followed by an effect which
            # does not have a section label.
            if section == 'Level':
                section = 'Effect'
                data[filetype][title][section] = ''

            # All fileypes: Color.
            # Colors are always single line and are sometimes followed by a Comment which
            # does not have a section label
            elif section == 'Color':
                section = 'Comment'
                if not data[filetype][title][section]:
                    data[filetype][title][section] = ''

            continue

        # Monographs: Requirements.
        # If we are parsing a requirements section and do not find a specially formatted requirement
        # entry, then we have moved on to the Effects section.
        # If we find one, append it to the requirements and we are done with this line.
        # Otherwise, we are now entering the Effect section
        elif filetype == 'Monographs' and section == 'Requirements':
            new_requirement = check_requirement(line)
            if new_requirement:
                data[filetype][title][section] += new_requirement
                continue
            else:
                section = 'Effect'
                data[filetype][title][section] = ''

        # under certain conditions, we need to use the previous line to detect a
        # change in section
        if (filetype == 'Ephemera' or filetype == 'Objects of Power') \
                and section == 'Form' \
                and check_multiline_section_boundary(line, previous_line):
            section = 'Effect'
            data[filetype][title][section] = ''

        # Objects of Power: Price. is multiline, but all lines contain money words.
        # So any line while looking for a price that does not have a money word is
        # actually the beginning of a comment.
        elif filetype == 'Objects of Power' and section == 'Price' and not check_money_words(line):
            section = 'Comment'
            data[filetype][title][section] = ''

        # we are in the multiline portion of a section, and should append
        # the current line to that section
        if data[filetype][title][section] == '':
            data[filetype][title][section] += line
        else:
            data[filetype][title][section] += ' ' + line

    return data


def check_for_filetype(line):
    """
    Check the current line for whether it reveals the current file's type or not.
    :param srtr line: the line to check
    :return: None or the string associated with this filetype's key ('Cantrips', 'Epherma'...)
    """

    if line == 'EPHEMERA OBJECTS':
        return "Ephemera"
    elif line == 'INCANTATIONS':
        return 'Incantations'
    elif line == 'OBJECTS OF POWER':
        return 'Objects of Power'
    elif line == 'SPELLS':
        return 'Spells'
    elif line == 'MONOGRAPHS':
        return 'Monographs'
    elif line == 'CHARACTER SECRETS':
        return 'Character Secrets'
    elif line == 'HOUSE SECRETS':
        return 'House Secrets'
    elif line == 'FORTE':
        return 'Forte'
    return None


def check_for_title(line):
    """
    Check the current line for whether it reveals the title of a new entry.
    :param srtr line: the line to check
    :return: tuple (the entry title, the entry type) or (None, None)
    """

    re_title = re.compile(
        '^(?P<title>.+) \\((?P<type>EPHEMERA OBJECT|SPELL|INCANTATION|OBJECT OF POWER|CONJURATION|INVOCATION|ENCHANTMENT|RITUAL|CHARACTER SECRETS|HOUSE SECRETS|FORTE ABILITY)\\)$')
    m = re_title.match(line)
    if m:
        return m.group('title'), m.group('type')
    return None, None


def parse_cantrip_line(line):
    """
    Parse a single line to determine if it contains a cantrip.
    Since the entire thing is on a single line, no state is required.
    :param str line: a single line of text
    :return: dict of dicts containing parsed data
    """

    data = {}

    re_cantrip = re.compile('^(?P<title>.+) \\((?P<type>CANTRIP|CHARM|SIGN|HEX)\\): (?P<effect>.+)$')
    m = re_cantrip.match(line)

    # Found a cantrip
    if m:
        data[m.group('title')] = {
            'Title': m.group('title'),
            'Type': m.group('type'),
            'Effect': m.group('effect')
        }

    return data

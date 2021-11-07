def save_tsv(data, filename):
    """
    Saves a data dict as a file in Tab Separated Value form.
    Newlines inside of values are replaced with " // " for readability in spreadsheets

    Where data follows the form:
    {
      {
        key: value1a
        key2: value1b\nvalue1bb
        key3: value1c
      },
      {
        key: value2a
        key2: value2b\nvalue2bb
        key3: value2c
      },
    }

    The output will be:
    key1\tkey2\tkey3
    value1a\tvalue1b // value1bb\tvalue1c
    value2a\tvalue2b // value2bb\tvalue2c

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
                # while writing, replace newlines with " // " so that the text will be readable
                # when viewed in a spreadsheet
                vals.append(' // '.join(data[k][ok].split("\n")))
            else:
                vals.append('')
        f.write("\t".join(vals) + "\n")
    f.close()

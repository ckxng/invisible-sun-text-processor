# Invisible Sun Text Processor

Read in Invisible Sun Kickstarter Text Reference files into structured formats. This is useful for building GM reference
spreadsheets and as input data for chat bots.

Place your text reference files in the _textreference_ directory

## Corrections

### 02-cantrips.txt

### SIGN AGAINST UNWANTED INFLUENCE

There is an extra break in the line. Remove the line break so that this entry is contained on a single line.

### 07-ephemera.txt

#### ANANYM

There is an extra blank line after the title of ANANYM. Remove this blank line.

#### SWAN'S SOUL

Most of the comments come after the color, which is always single-line. However, SWAN'S SOUL does not because it also
has a depletion. This creates an exception which causes complications when parsing.

Change the text:

    Color: Indigo
    Depletion: Ends automatically when
    the sun next sets
    Empath, page 68
    THE KEY

To:

    Color: Indigo
    Empath, page 68
    THE KEY
    Depletion: Ends automatically when
    the sun next sets

This will allow the text to parse correctly.
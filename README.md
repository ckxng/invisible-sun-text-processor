# Invisible Sun Text Processor

Read in Invisible Sun Kickstarter Text Reference files and output structured CSV and JSON data.

Place your text reference files in the _textreference_ directory

## Corrections

### 07-ephemera.txt
#### ANANYM
There is an extra blank line after the title of ANANYM.  Remove this blank line.
#### SWAN'S SOUL
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
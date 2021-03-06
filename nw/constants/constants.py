# -*- coding: utf-8 -*-
"""novelWriter Constants

 novelWriter – Constants
=========================
 Constants for translating flags and enums to text

 File History:
 Created: 2019-04-28 [0.0.1]

"""

from nw.constants.enum import nwItemClass, nwItemLayout

class nwConst():

    tStampFmt = "%Y-%m-%d %H:%M:%S"

# END Class nwConst

class nwFiles():

    APP_ICON   = "novelWriter.svg"
    PROJ_FILE  = "nwProject.nwx"
    PROJ_DICT  = "wordlist.txt"
    SESS_INFO  = "sessionInfo.log"
    INDEX_FILE = "tagsIndex.json"
    EXPORT_OPT = "exportOptions.json"
    TLINE_OPT  = "timelineOptions.json"
    SLOG_OPT   = "sessionLogOptions.json"
    MERGE_OPT  = "docMergeOptions.json"

# END Class nwFiles

class nwKeyWords:

    TAG_KEY    = "@tag"
    POV_KEY    = "@pov"
    CHAR_KEY   = "@char"
    PLOT_KEY   = "@plot"
    TIME_KEY   = "@time"
    WORLD_KEY  = "@location"
    OBJECT_KEY = "@object"
    ENTITY_KEY = "@entity"
    CUSTOM_KEY = "@custom"

# END Class nwKeyWords

class nwLabels():

    CLASS_NAME = {
        nwItemClass.NO_CLASS  : "None",
        nwItemClass.NOVEL     : "Novel",
        nwItemClass.PLOT      : "Plot",
        nwItemClass.CHARACTER : "Characters",
        nwItemClass.WORLD     : "Locations",
        nwItemClass.TIMELINE  : "Timeline",
        nwItemClass.OBJECT    : "Objects",
        nwItemClass.ENTITY    : "Entity",
        nwItemClass.CUSTOM    : "Custom",
        nwItemClass.TRASH     : "Trash",
    }
    CLASS_FLAG = {
        nwItemClass.NO_CLASS  : "0",
        nwItemClass.NOVEL     : "N",
        nwItemClass.PLOT      : "P",
        nwItemClass.CHARACTER : "C",
        nwItemClass.WORLD     : "L",
        nwItemClass.TIMELINE  : "T",
        nwItemClass.OBJECT    : "O",
        nwItemClass.ENTITY    : "E",
        nwItemClass.CUSTOM    : "X",
        nwItemClass.TRASH     : "R",
    }
    LAYOUT_NAME = {
        nwItemLayout.NO_LAYOUT  : "None",
        nwItemLayout.TITLE      : "Title Page",
        nwItemLayout.BOOK       : "Book",
        nwItemLayout.PAGE       : "Plain Page",
        nwItemLayout.PARTITION  : "Partition",
        nwItemLayout.UNNUMBERED : "Unnumbered",
        nwItemLayout.CHAPTER    : "Chapter",
        nwItemLayout.SCENE      : "Scene",
        nwItemLayout.NOTE       : "Note",
    }
    LAYOUT_FLAG = {
        nwItemLayout.NO_LAYOUT  : "Xo",
        nwItemLayout.TITLE      : "Tt",
        nwItemLayout.BOOK       : "Bk",
        nwItemLayout.PAGE       : "Pg",
        nwItemLayout.PARTITION  : "Pt",
        nwItemLayout.UNNUMBERED : "Un",
        nwItemLayout.CHAPTER    : "Ch",
        nwItemLayout.SCENE      : "Sc",
        nwItemLayout.NOTE       : "Nt",
    }
    KEY_NAME = {
        nwKeyWords.TAG_KEY    : "Tag",
        nwKeyWords.POV_KEY    : "Point of View",
        nwKeyWords.CHAR_KEY   : "Characters",
        nwKeyWords.PLOT_KEY   : "Plot",
        nwKeyWords.TIME_KEY   : "Time",
        nwKeyWords.WORLD_KEY  : "Locations",
        nwKeyWords.OBJECT_KEY : "Objects",
        nwKeyWords.ENTITY_KEY : "Entities",
        nwKeyWords.CUSTOM_KEY : "Custom",
    }

# END Class nwLabels

class nwDependencies():
    """Python package dependencies and their reference links.
    """
    PACKS = {
        "pyqt5"      : {
            "site" : "",
            "docs" : "",
        },
        "lxml"       : {
            "site" : "",
            "docs" : "",
        },
        "pyenchant"  : {
            "site" : "",
            "docs" : "",
        },
        "latexcodec" : {
            "site" : "https://pypi.org/project/latexcodec/",
            "docs" : "https://latexcodec.readthedocs.io/en/latest/",
        },
        "pypandoc" : {
            "site" : "https://pypi.org/project/pypandoc/",
            "docs" : "https://pypi.org/project/pypandoc/",
        },
    }

# END Class nwDependencies

class nwQuotes():
    """Allowed quotation marks.
    Source: https://en.wikipedia.org/wiki/Quotation_mark
    """

    SYMBOLS = [
        "\u0022", # Quotation mark
        "\u0027", # Apostrophe
        "\u00ab", # Left-pointing double angle quotation mark
        "\u00bb", # Right-pointing double angle quotation mark
        "\u2018", # Left single quotation mark
        "\u2019", # Right single quotation mark
        "\u201a", # Single low-9 quotation mark
        "\u201b", # Single high-reversed-9 quotation mark
        "\u201c", # Left double quotation mark
        "\u201d", # Right double quotation mark
        "\u201e", # Double low-9 quotation mark
        "\u201f", # Double high-reversed-9 quotation mark
        "\u2039", # Single left-pointing angle quotation mark
        "\u203a", # Single right-pointing angle quotation mark
        "\u2e42", # Double low-reversed-9 quotation mark
        "\u300c", # Left corner bracket
        "\u300d", # Right corner bracket
        "\u300e", # Left white corner bracket
        "\u300f", # Right white corner bracket
    ]

# END Class nwQuotes

class nwUnicode:
    """Suppoted unicode character constants and translation maps.
    """

    # Unicode Constants

    ## Quotation Marks
    U_QUOT   = "\u0022" # Quotation mark
    U_APOS   = "\u0027" # Apostrophe
    U_LAQUO  = "\u00ab" # Left-pointing double angle quotation mark
    U_RAQUO  = "\u00bb" # Right-pointing double angle quotation mark
    U_LSQUO  = "\u2018" # Left single quotation mark
    U_RSQUO  = "\u2019" # Right single quotation mark
    U_SBQUO  = "\u201a" # Single low-9 quotation mark
    U_SUQUO  = "\u201b" # Single high-reversed-9 quotation mark
    U_LDQUO  = "\u201c" # Left double quotation mark
    U_RDQUO  = "\u201d" # Right double quotation mark
    U_BDQUO  = "\u201e" # Double low-9 quotation mark
    U_UDQUO  = "\u201f" # Double high-reversed-9 quotation mark
    U_LSAQUO = "\u2039" # Single left-pointing angle quotation mark
    U_RSAQUO = "\u203a" # Single right-pointing angle quotation mark
    U_BDRQUO = "\u2e42" # Double low-reversed-9 quotation mark
    U_LCQUO  = "\u300c" # Left corner bracket
    U_RCQUO  = "\u300d" # Right corner bracket
    U_LWCQUO = "\u300e" # Left white corner bracket
    U_RECQUO = "\u300f" # Right white corner bracket

    ## Punctuation
    U_ENDASH = "\u2013" # Short dash
    U_EMDASH = "\u2014" # Long dash
    U_HELLIP = "\u2026" # Ellipsis

    ## Other
    U_NBSP   = "\u00a0" # Non-breaking space
    U_PARA   = "\u2029" # Paragraph separator

    # HTML Equivalents

    ## Quotes
    H_QUOT   = "&quot;"
    H_APOS   = "&#39;"
    H_LAQUO  = "&laquo;"
    H_RAQUO  = "&raquo;"
    H_LSQUO  = "&lsquo;"
    H_RSQUO  = "&rsquo;"
    H_SBQUO  = "&sbquo;"
    H_SUQUO  = "&#8219;"
    H_LDQUO  = "&ldquo;"
    H_RDQUO  = "&rdquo;"
    H_BDQUO  = "&bdquo;"
    H_UDQUO  = "&#8223;"
    H_LSAQUO = "&lsaquo;"
    H_RSAQUO = "&rsaquo;"
    H_BDRQUO = "&#11842;"
    H_LCQUO  = "&#12300;"
    H_RCQUO  = "&#12301;"
    H_LWCQUO = "&#12302;"
    H_LWCQUO = "&#12302;"

    ## Punctuation
    H_ENDASH = "&ndash;"
    H_EMDASH = "&mdash;"
    H_HELLIP = "&hellip;"

    ## Other
    H_NBSP   = "&nbsp;"

# END Class nwUnicode

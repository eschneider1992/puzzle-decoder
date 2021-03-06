#!/usr/bin/python3

import collections


# Best key so far:
# ./solver.py --polish-key '((4, "e"), (16, "s"), (2, "a"), (14, "i"), (1, "t"), (8, "o"), (5, "n"), (9, "r"), (10, "l"), (6, "d"), (7, "c"), (19, "u"), (12, "h"), (21, "y"), (15, "b"), (3, "m"), (13, "g"), (11, "f"), (20, "p"), (29, "v"), (17, "w"), (18, "k"), (33, "j"), (24, "q"))'

PRESUMED_ANSWER = ((4, "e"), (16, "s"), (2, "a"), (14, "i"), (1, "t"), (8, "o"), (5, "n"), (9, "r"), (10, "l"), (6, "d"), (7, "c"), (19, "u"), (12, "h"), (15, "b"), (21, "y"), (3, "m"), (13, "g"), (11, "f"), (29, "v"), (20, "p"), (17, "w"), (18, "k"), (24, "q"), (33, "j"))


with open("/usr/share/dict/words") as word_file:
    _english = set(word.strip().lower() for word in word_file)


# Words that are in the dictionary that I am removing from consideration
# (Most of these are populated using the solver --show-words-only arg)
BLACKLIST = set([
    "th", "ob", "li", "pei", "rn", "cali", "ani", "au", "sn", "ts", "os", "rs",
    "es", "nth", "o", "ti", "lind", "mo", "zed", "mani", "sh", "sade", "ni",
    "hg", "les", "ac", "zane", "ho", "ann", "si", "noe", "zr", "kate", "ur",
    "tare", "tsars", "jain", "pate", "mads", "al", "saar", "fa", "che", "hes",
    "em", "eco", "mi", "hob", "ben", "ci", "len","ra", "jon", "mira", "ned",
    "md", "mg", "leo", "oz", "fain", "ah",  "laue", "wot", "fay", "roy", "mu",
    "nu", "fez", "np", "sol", "rho", "pd", "ag", "mel", "gad", "ito", "la",
    "lam", "loth", "tads", "hz", "ref", "cain", "di", "ibo", "sb", "ay", "fer",
    "rio", "ado", "nd", "ed", "di", "yo", "ty", "eh", "val", "hos", "e","jo",
    "ken", "re", "cary", "ow", "lo", "aft", "cid", "l", "oh", "ins", "mn",
    "lon", "kr", "mes", "hans", "par", "id", "rood", "moog", "joe", "zn", "na",
    "carl", "noh", "ad", "vegas", "howe", "lew", "mil", "sago", "se", "hart",
    "dos", "rep", "cains", "las", "se", "siva", "pone", "gte", "johns",
    "glaser", "ted", "hbo", "thanh", "cato", "iso", "dec", "ca", "hew", "faye",
    "jan", "asp", "hep", "bah", "lea", "zion", "yale", "le" "devin", "bate",
])


# Words not in English but known part of the solution
KNOWN_GOOD = set([
    "illithid", "askelios", "areksul", "aundaire", "goblinoids", "agression",
    "choas"
])


def is_english(word):
    word = word.lower()
    return (
        word in _english and word not in BLACKLIST or
        word in KNOWN_GOOD
    )


ASSUMED = {
    22: "9",
    23: "4",
    25: "7",
    26: "1",
    27: "6",
    28: "8",
    30: "3",
    31: "2",
    32: "5",
    34: "0",

    40: " ",
    41: ":",
    42: ",",
    43: "\n",
    44: ".",
}


GUESSES = {
    # This is the only one ever found as a single character
    2: ("a", "i"),
}


CHARACTERS = (
    # Title
    1, 12, 4, 40,
    14, 5, 29, 2, 16, 14, 8, 5, 40,
    8, 11, 40,
    2, 19, 5, 6, 2, 14, 9, 4, 43,

    # Number
    26, 41, 40,
    4, 16, 1, 2, 15, 10, 14, 16, 12, 40,
    14, 10, 10, 14, 1, 12, 14, 6, 40,
    8, 5, 40,
    1, 12, 4, 40,
    20, 10, 2, 5, 4, 1, 40,

    2, 5, 6, 40,
    7, 9, 4, 2, 1, 4, 40,
    2, 40,
    15, 2, 16, 4, 40,
    11, 8, 9, 40,
    15, 9, 4, 4, 6, 14, 5, 13, 43,

    # Repeated
    16, 19, 7, 7, 4, 16, 16, 40,
    20, 9, 8, 15, 2, 15, 14, 10, 14, 1, 21, 41, 40,
    22, 28, 43,

    # Number
    31, 41, 40,
    16, 19, 15, 33, 4, 7, 1, 40,
    12, 19, 3, 2, 5, 8, 14, 6, 16, 40,
    1, 8, 40,
    14, 5, 1, 4, 10, 10, 4, 7, 1, 40,

    6, 4, 29, 8, 19, 9, 4, 9, 16, 42, 40,
    4, 16, 1, 2, 15, 10, 14, 16, 12, 40,
    16, 4, 4, 6, 16, 40,
    8, 11, 40,
    2, 13, 9, 4, 16, 16, 14, 8, 5, 43,

    # Repeated
    16, 19, 7, 7, 4, 16, 16, 40,
    20, 9, 8, 15, 2, 15, 14, 10, 14, 1, 21, 41, 40,
    28, 30, 43,

    # Number
    30, 41, 40,
    16, 19, 15, 33, 4, 7, 1, 40,
    13, 8, 15, 10, 14, 5, 8, 14, 6, 16, 40,
    1, 8, 40,
    14, 5, 1, 4, 10, 10, 4, 7, 1, 40,

    6, 4, 29, 8, 19, 9, 4, 9, 16, 42, 40,
    4, 16, 1, 2, 15, 10, 14, 16, 12, 40,
    16, 4, 4, 6, 16, 40,
    8, 11, 40,
    16, 21, 3, 20, 2, 1, 12, 21, 43,

    # Repeated
    16, 19, 7, 7, 4, 16, 16, 40,
    20, 9, 8, 15, 2, 15, 14, 10, 14, 1, 21, 41, 40,
    22, 27, 43,

    # Number
    23, 41, 40,
    11, 8, 19, 5, 6, 40,
    1, 12, 4, 40,
    2, 9, 3, 21, 40,
    8, 11, 40,
    1, 12, 4, 40,
    9, 4, 6, 40,
    12, 2, 5, 6, 40,

    8, 11, 40,
    6, 8, 8, 3, 43,

    # Repeated
    16, 19, 7, 7, 4, 16, 16, 40,
    20, 9, 8, 15, 2, 15, 14, 10, 14, 1, 21, 41, 40,
    25, 26, 43,

    # Number
    32, 41, 40,
    7, 8, 5, 24, 19, 4, 9, 40,
    2, 5, 6, 40,
    6, 4, 16, 1, 9, 8, 21, 40,
    1, 12, 4, 40,
    7, 14, 1, 21, 40,
    8, 11, 40,

    2, 16, 18, 4, 10, 14, 8, 16, 43,

    # Repeated
    16, 19, 7, 7, 4, 16, 16, 40,
    20, 9, 8, 15, 2, 15, 14, 10, 14, 1, 21, 41, 40,
    25, 22, 43,

    # Page 2
    # Number
    27, 41, 40,
    1, 2, 3, 4, 40,
    2, 5, 6, 40,
    13, 2, 14, 5, 40,
    7, 8, 5, 1, 9, 8, 10, 40,
    8, 11, 40,
    1, 12, 4, 40,

    15, 4, 2, 16, 1, 40,
    15, 4, 10, 8, 17, 40,
    2, 16, 18, 4, 10, 14, 8, 16, 43,

    # Repeated
    16, 19, 7, 7, 4, 16, 16, 40,
    20, 9, 8, 15, 2, 15, 14, 10, 14, 1, 21, 41, 40,
    22, 23, 43,

    # Number
    25, 41, 40,
    7, 8, 5, 24, 19, 4, 9, 40,
    2, 5, 6, 40,
    6, 4, 16, 1, 9, 8, 21, 40,
    1, 12, 4, 40,
    7, 14, 1, 21, 40,
    8, 11, 40,

    2, 9, 4, 18, 16, 19, 10, 43,

    # Repeated
    16, 19, 7, 7, 4, 16, 16, 40,
    20, 9, 8, 15, 2, 15, 14, 10, 14, 1, 21, 41, 40,
    25, 26, 43,

    # Number
    28, 41, 40,
    14, 5, 14, 1, 14, 2, 1, 4, 40,
    2, 40,
    11, 4, 2, 9, 16, 8, 3, 4, 42, 40,
    19, 5, 16, 19, 7, 7, 4, 16, 16, 11, 19, 10, 40,

    2, 16, 16, 2, 19, 10, 1, 40,
    8, 5, 40,
    11, 2, 14, 9, 12, 2, 29, 4, 5, 42, 40,
    15, 10, 8, 8, 6, 21, 40,
    4, 5, 8, 19, 13, 12, 40,
    1, 8, 40,

    16, 1, 2, 9, 1, 40,
    2, 40,
    17, 2, 9, 43,

    # Repeated
    16, 19, 7, 7, 4, 16, 16, 40,
    20, 9, 8, 15, 2, 15, 14, 10, 14, 1, 21, 41, 40,
    22, 27, 43,

    # Number
    22, 41, 40,
    14, 5, 40,
    1, 12, 4, 40,
    7, 12, 8, 2, 16, 40,
    8, 11, 40,
    17, 2, 9, 42, 40,
    16, 4, 7, 9, 4, 1, 10, 21, 40,

    14, 5, 16, 1, 2, 10, 10, 40,
    1, 12, 4, 40,
    14, 10, 10, 14, 1, 12, 14, 6, 40,
    2, 16, 40,
    9, 19, 10, 4, 9, 16, 40,
    8, 11, 40,

    11, 2, 14, 9, 12, 2, 29, 4, 5, 43,

    # Repeated
    16, 19, 7, 7, 4, 16, 16, 40,
    20, 9, 8, 15, 2, 15, 14, 10, 14, 1, 21, 41, 40,
    22, 30, 43,

    # Number
    26, 34, 41, 40,
    6, 14, 16, 7, 2, 9, 6, 40,
    2, 10, 10, 40,
    16, 4, 7, 9, 4, 7, 21, 44, 40,
    10, 4, 1, 40,
    1, 12, 4, 40,

    17, 2, 9, 40,
    17, 14, 1, 12, 40,
    12, 19, 3, 2, 5, 14, 1, 21, 40,
    15, 4, 13, 14, 5, 44,
)

# Set of unknown characters
UNKNOWN = set(CHARACTERS) - set(ASSUMED.keys())

# Tuple of all words
_words = []
_word = []
for _character in CHARACTERS:
    if _character in ASSUMED:
        if _word:
            _words.append(tuple(_word))
            _word = []
    else:
        _word.append(_character)
WORDS = tuple(_words)
# Counter object of all characters and words
CHARACTER_FREQ = collections.Counter([character for character in CHARACTERS
                                      if character not in ASSUMED])
WORD_FREQ = collections.Counter(WORDS)

# Set of unique words
WORD_SET = set(WORDS)
# Counter object of characters in the word set (to avoid influence by repeated
# phrases)
_word_set_characters = []
for _word in WORD_SET:
    _word_set_characters.extend(list(_word))
SET_FREQ = collections.Counter(_word_set_characters)


# English letters sorted, from here:
# http://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
ENGLISH_FREQ_LIST = ("e", "t", "a", "o", "i", "n", "s", "r", "h", "d", "l",
                     "u", "c", "m", "f", "y", "w", "g", "p", "b", "v", "k",
                     "x", "q", "j", "z")
# Get the two lists of frequency-sorts cipher characters (different assumptions
# on their base data)
CHARACTER_FREQ_LIST = [
    key for key, value in
    sorted(CHARACTER_FREQ.items(), key=lambda x: x[1], reverse=True)
]
SET_FREQ_LIST = [
    key for key, value in
    sorted(SET_FREQ.items(), key=lambda x: x[1], reverse=True)
]


# Example of how keys look (could be up to 26 pairs long)
SAMPLE_KEY = ((2, "a"), (1, "t"), (12, "h"), (4, "e"), (8, "o"), (11, "f"))


if __name__ == "__main__":
    import ipdb; ipdb.set_trace()

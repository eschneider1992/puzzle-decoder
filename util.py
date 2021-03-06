#!/usr/bin/python3

from ast import literal_eval
import collections
import cv2
import numpy
import string

import data


# The maximum size each individual character can be
SHAPE = (90, 70, 3)
# The height to allow for cv2.putText
TEXT_BUFFER = 40
# The height to allow for each row of character + text
LINE_BUFFER = TEXT_BUFFER + 10
# Tracks the current spot where we are inserting characters
Cursor = collections.namedtuple('Cursor', ['x', 'ymin', 'ymax'])


def check_characters_with_image(characters, assumed, mapping=None):
    """
    Writes image of stored characters for visual checking. Each line of text is
    represented as
        1) A line of the cipher text
        2) Underneath it, our mapping of cipher to ascii (? by default)

    Arguments:
        mapping: None (in which case all non-assumed characters become "?") or
            a dictionary of {unknown character (int): ascii}, where the unknown
            characters are all stored as integers in CHARACTERS. Items in the
            mapping will be displayed as such under the sipher text.

    Returns nothing
    """

    # Note that in image space it goes (y, x), a.k.a. (vertical, horizontal)

    # First make a blank canvas to insert images into
    image = numpy.ones((70 * (SHAPE[0] + LINE_BUFFER), 70 * SHAPE[1], 3)) * 255
    # Make a cursor tracking the next position to add a character
    cursor = Cursor(x=0, ymin=0, ymax=SHAPE[0])

    # Add each character to the image
    for character in characters:

        # If we get a newline, update the cursor. If not, place a character
        if character in assumed and assumed[character] == "\n":
            # Zero the x position and bump the height down
            cursor = Cursor(x=0,
                            ymin=cursor.ymax + LINE_BUFFER,
                            ymax=cursor.ymax + LINE_BUFFER + SHAPE[0])

        else:
            # Load the image for this character. This is probably inefficient,
            # but since this function is meant for human inspection anyway the
            # possible lengths won't matter to a computer
            character_image = cv2.imread(
                "images/image_{}.png".format(character)
            )

            # Calculate where the image should be placed vertically so that it
            # will be centered on the cursor. The character images have
            # variable heights depending on the character shape
            character_y_edge = calculate_y_edge(cursor, character_image.shape)

            # Set the character image into the greater image
            # Note that images are (y, x), where x and y are in the human
            # expected frame
            image[character_y_edge:character_y_edge + character_image.shape[0],
                  cursor.x:cursor.x + character_image.shape[1],
                  :] = character_image

            # Figure out what we want to map cipher text to, this display it
            # underneath the cipher representation
            if character in assumed:
                text = assumed[character]
            else:
                if mapping and character in mapping:
                    text = mapping[character]
                else:
                    text = "?"
            cv2.putText(
                img=image,
                text=text,
                # WTF - why is putText location in (horizontal, vertical)?
                org=(cursor.x + character_image.shape[1] // 4,
                     cursor.ymax + TEXT_BUFFER),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1.5,
                color=(0, 0, 0),
                thickness=2,
            )

            # Update the cursor
            cursor = Cursor(x=cursor.x + character_image.shape[1],
                            ymin=cursor.ymin,
                            ymax=cursor.ymax)

    # Figure out where we start hitting blank whitespace, and clip the image
    where = numpy.argwhere(image != (255, 255, 255))
    y_edge = max(where[:, 0]) + 20
    x_edge = max(where[:, 1]) + 20
    image = image[0:y_edge, 0:x_edge]

    # Write out the image
    cv2.imwrite("check_text_image.png", image)


def calculate_y_edge(cursor, shape):
    # Get the range and subtract the character size
    empty = (cursor.ymax - cursor.ymin) - shape[0]
    return cursor.ymin + int(empty / 2)


def sample_exponential():
    """
    Generator to get exponential samples. Done in batches because the random
    generator is a lot faster per sample that way, compared to one call per
    sample.

    Samples are scaled to be *mostly* from 0.0-1.0, and then samples over 1.0
    are remove so we get an approximate 1/x distribution, but capped at 1.0
    """
    while True:
        batch = numpy.random.exponential(scale=0.2, size=int(1e4))
        for value in batch:
            if value <= 1.0:
                yield value


def map_characters(characters, key):
    """
    Takes a tuple of characters and returns the same, but with swapped values,
    according to the given mapping AND to the assumed mapping in data.ASSUMED
    using whitespace, punctuation, and numbers

    Arguments:
        characters: tuple of ciphertext characters (integers)
        key: tuple of tuple pairs containing (cipher character, ascii). Does
            not need to map all 26 letters

    Returns:
        same structure as characters, but some or all of the cipher characters
        have been swapped for the ascii characters via key and data.ASSUMED
    """
    mapping = dict(key)
    new_characters = []
    for character in characters:
        if character in data.ASSUMED:
            new_characters.append(data.ASSUMED[character])
        elif character in mapping:
            new_characters.append(mapping[character])
        else:
            new_characters.append(character)
    return tuple(new_characters)


def map_words(words, key):
    """
    Takes a tuple of tuples and returns the same, but with swapped values,
    according to the given mapping

    Arguments:
        words: tuple of tuple of ciphertext characters (integers)
        key: tuple of tuple pairs containing (cipher character, ascii). Does
            not need to map all 26 letters

    Returns:
        same structure as words, but some or all of the cipher characters have
        been swapped for the ascii characters via key
    """
    mapping = dict(key)
    new_words = []
    for word in words:
        new_words.append(
            tuple([mapping[character] if character in mapping else character
                   for character in word])
        )
    return tuple(new_words)


def score_key(mapped, key):
    """
    Calculate the score by the number of English words.

    Arguments:
        words: see map_words output
        key: see map_words

    Returns:
        float, number from 0-1 indicated how many of the mapped words were
        English
    """
    count = 0
    for word in mapped:
        try:
            string_word = "".join(word)
            if data.is_english(string_word):
                count += 1
        except TypeError:
            pass
    return count / len(mapped)


def check_key(checked_keys, words, key):
    """
    Scores a given key by ranking the fraction of English in words created
    by the key, then stores that mapping in checked_keys.

    Arguments:
        checked_keys: dict, contains {tuple key: float score}
        words: see map_words
        key: see map_words

    Returns:
        mapped: see map_words return value
        score: float

    Note that the dictionary checked_keys is modified
    """

    # Switch characters we know we want to map
    mapped = map_words(words, key)

    # Get the score in a reliable way
    score = score_key(mapped, key)

    # Record the checked key and its score. Note that we have to set the keys
    # to be strings so we can jsonify them
    checked_keys[str(key)] = score

    return mapped, score


def display_key(key, include_characters=False, score=None):
    """Render a key onto the whole dataset."""
    mapped = list(map_characters(data.CHARACTERS, key))
    for idx in range(len(mapped)):
        if not isinstance(mapped[idx], str):
            removed = mapped.pop(idx)
            if include_characters:
                mapped.insert(idx, ".{}.".format(removed))
            else:
                mapped.insert(idx, "?")

    # Do some visual formatting in the include_characters case
    joined = "".join(mapped)
    if include_characters:
        joined = joined.replace("..", ".")
        joined = joined.replace(" .", " ").replace(". ", " ")
        joined = joined.replace(" ", "   ")

    # Get a common ending
    postfix = "Unexplained characters:\n{}\n{}\n".format(
        unexplained_letters(key), key
    ) + joined

    if score is None:
        return postfix
    else:
        return "score: {:.4f}\n".format(score) + postfix


def get_english_words(key):
    """Return a set of only the full words that went into the score."""
    words = set()
    mapped = map_words(data.WORD_SET, key)

    for word in mapped:
        try:
            string_word = "".join(word)
            if data.is_english(string_word):
                words.add(string_word)
        except TypeError:
            pass

    return words


def unexplained_letters(key):
    included = [pair[1] for pair in key]
    unexplained = set()
    for letter in string.ascii_lowercase:
        if letter not in included:
            unexplained.add(letter)
    return unexplained


def get_word_pairs(key):
    """Return a list of cipher/ascii pairs that were part of full words."""
    valid_letters = set()
    for word in get_english_words(key):
        for letter in word:
            valid_letters.add(letter)
    pairs = []
    for pair in key:
        if pair[1] in valid_letters:
            pairs.append(pair)
    return tuple(pairs)


RankedKey = collections.namedtuple('RankedKey', ['key', 'score'])


def get_ranked_keys(checked_keys, number=1):
    """
    Get the top N ranked keys from a dictionary.

    Arguments:
        checked_keys: a dictionary of keys and scores, as from
            checked_keys_dictionary.json
        number: number of ranked scores we want to extract

    Returns:
        A tuple of (list of ranked keys, list of corresponding scores)
    """
    assert number >= 1
    ranked_keys = [RankedKey(key=None, score=0.0)] * number

    for key, score in checked_keys.items():
        # If the current score is greater than the least score in the ranked
        # list, then replace that least score and then resort the list.
        if score > ranked_keys[-1].score:
            ranked_keys[-1] = RankedKey(key, score)
            ranked_keys = sorted(ranked_keys,
                                 key=lambda x: x.score,
                                 reverse=True)

    # We should work with string keys (for the JSON dump) and for non-string
    # keys (like in a dynamic key tracking)
    try:
        return ([literal_eval(key.key) for key in ranked_keys],
                [key.score for key in ranked_keys])
    except ValueError:
        return ([key.key for key in ranked_keys],
                [key.score for key in ranked_keys])


def generate_random_key(RNG, checked_keys, length, frozen=None):
    """
    Create a random key, sampled from likely letters, of given length.

    Arguments:
        RNG: Generator that produces a float from 0 to 1, waited towards 0
            with the exponential distribution. The purpose is to use it to
            preferentially sample letters on the likely side of the frequency
            sorted list
        checked_keys: a dictionary of keys and scores, as from
            checked_keys_dictionary.json
        length: int, length of key to create
        frozen: tuple of tuple pairs (like a key) containing cipher and ascii
            pairs that we want to force into the key

    Returns:
        A key of the normal format, a tuple of tuple pairs containing
            (cipher character, ascii letter). Should be sorted so that cipher
            characters are in the same order as data.SET_FREQ_LIST, for key
            comparability
    """
    key = []

    # Make a list of the frequency analyzed letters (cipher and ascii) so that
    # elements can be popped
    sample_characters = list(data.SET_FREQ_LIST)
    sample_letters = list(data.ENGLISH_FREQ_LIST)

    # Freeze certain pairs
    if frozen is not None:
        for character, letter in frozen:
            # Add the pair to the key
            key.append((character, letter))
            # Remove the pair from the sample lists
            sample_characters.pop(sample_characters.index(character))
            sample_letters.pop(sample_letters.index(letter))

    # Critically (maybe), for each key we want to map the *first* character
    # with a sampled letter.
    # Con: That means for a key of length 10 we will always map the same 10
    #   characters. Maybe we should sample randomly from both lists?
    # Pro: As-is, the characters will always be in a repeatable order. That
    #   means that we don't have to deal with key uniqueness issues.
    # Note: We *definitely* don't want to pop the same index from each list,
    #   (that would always be the same mapping but with differently ordered
    #   pairs) but we could take two samples
    while (len(key) < length and
            len(sample_characters) > 0 and
            len(sample_letters) > 0):
        sample = next(RNG)
        index = int(round(sample * len(sample_letters))) - 1
        key.append(
            (
                sample_characters.pop(0),
                sample_letters.pop(index)
            )
        )

    # Sort it so the cipher characters are in frequency order (for key
    # comparability)
    key = sorted(key, key=lambda x: data.SET_FREQ_LIST.index(x[0]))

    # Tuplify it to lock it in place and make it dictionaryable
    key = tuple(key)

    # If we have a collision, recurse and keep trying. Note that this also
    # provides a natural limit to the number of attempts, since there is a
    # recursion limit
    while str(key) in checked_keys:
        key = generate_random_key(RNG, checked_keys, length)

    return key


def polish_known_key(RNG, checked_keys, words, key, n_depth=100,
                     n_breadth=100):
    """
    Try permuting all of the pairs in key that are *not currently* part of an
    English word. The intent is to ignore presumed good stuff and narrow in
    on the unknown areas.

    Arguments:
        RNG: See generate_random_key docstring
        checked_keys: See check_key docstring. This is the master dictionary
            tracking which keys have been seen and their score
        words: See map_words docstring
        key: See generate_random_key docstring, this would be the output
        n_depth: int, number of times to take the latest best key
        n_breadth: int, number of times to try on a given key before moving
            onto the current highest ranked one

    Returns: Nothing. All that happens is checked_keys is updated
    """

    # Track the keys generated as part of this endeavor
    keys = { key: score_key(map_words(words, key), key) }

    # Spend a while trying variations on the given key
    for _ in range(n_depth):
        top_keys, _ = get_ranked_keys(keys, number=1)
        frozen = get_word_pairs(top_keys[0])
        for _ in range(n_breadth):
            # Generate a new key with certain values frozen
            new_key = generate_random_key(RNG,
                                          checked_keys,
                                          length=26,
                                          frozen=frozen)
            _, score = check_key(checked_keys, words, new_key)

            # Maintain a local structure of tried keys so we can get the top
            # keys from our search area instead of from the global pool
            keys[str(new_key)] = score

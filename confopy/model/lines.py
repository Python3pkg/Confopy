# coding: utf-8
'''
File: lines.py
Author: Oliver Zscheyge
Description:
    Utility methods to handle lines (list of unicode strings).
'''

import operator
import re
from functools import reduce

def lines2unicode(lines=[], strip=False, sep="\n"):
    """Converts a list of strings to a single unicode string.
    Args:
        lines: The list of unicode strings to convert.
        strip: Boolean. Strip the lines and the resulting string?
        sep:   Line separator.
    Return:
        A single unicode string.
    """
    if strip:
        return reduce(lambda a, b: a.strip() + sep + b.strip(), lines, "").strip()
    return reduce(lambda a, b: a + sep + b, lines, "")[1:]

def is_empty(lines):
    """Checks whether a list of ustrings is empty.
    Args:
        lines: List of unicode strings.
    Return:
        True if list is empty or contains whitespace strings only.
        False otherwise.
    """
    if lines == [] or lines2unicode(lines).strip() == "":
        return True
    return False

def match(regex, lines, strip=False):
    """Convenience method converting a list of lines to a single unicode
    string then matching a regex.
    Args:
        regex: Regular expression.
        lines: List of unicode strings.
        strip: Boolean flag whether to strip each line from whitespace.
    Return:
        True if the text represented by lines matches regex. False otherwise.
    """
    return re.match(regex, lines2unicode(lines, strip), re.U)

def match_each(regex, lines, strip=False):
    """Returns true if regex matches for each line.
    Args:
        regex: Regular expression.
        lines: List of unicode strings.
        strip: Boolean flag whether to strip each line from whitespace.
    Return:
        True if each line matches regex. False otherwise.
    """
    for line in lines:
        if strip:
            line = line.strip()
        if not re.match(regex, line, re.U):
            return False

    if lines == [] and regex != r"":
        return False
    return True

def lines_using(lines, words, strip=False, sep=" "):
    """
    Args:
        lines: List of unicode strings.
        words: List of unicode strings.
        strip: Boolean flag whether to strip each line from whitespace.
        sep:   Unicode string indicating the separator between words in
               the lines parameter.
    Return:
        The number of lines from the beginning being fully and only
        composed by words from parameter words.
    """
    line_count = 0
    for line in lines:
        if strip:
            line = line.strip()
        if line != "":
            line_words = line.split(sep)
            for word in [w for w in line_words if w != ""]:
                if word not in words:
                    return line_count
            line_count += 1
    return line_count

def words_using(lines, words, strip=False, sep=" "):
    """
    Args:
        See #lines_using.
    Return:
        The number of consecutive words from the beginning that are
        contained in the parameter words.
    """
    word_count = 0
    for line in lines:
        if strip:
            line = line.strip()
        if line != "":
            line_words = line.split(sep)
            for word in [w for w in line_words if w != ""]:
                if word not in words:
                    return word_count
                word_count += 1
    return word_count

def avg_word_length(lines):
    """Computes the average word length.
    Args:
        lines: List of unicode strings.
    """
    words = lines2unicode(lines, True, " ").split()
    wc = 0.0
    wl = 0.0
    for w in words:
        w = w.strip()
        wl += len(w)
        if w != "":
            wc += 1
    if wc > 0.0:
        return wl / wc
    return 0.0

def avg_words_per_line(lines):
    """Computes the average amount of words per line.
    Args:
        lines: List of unicode strings.
    """
    if len(lines) > 0:
        return reduce(operator.add, [len(line.split()) for line in lines], 0) / float(len(lines))
    return 0.0




if __name__ == '__main__':
    print("Test for " + __file__)

    l0 = []
    l0_expected = ""
    l1 = ["Hello World!"]
    l1_expected = "Hello World!"
    l2 = ["Hello World,", "how are you?", "Sincerely", "Universe"]
    l2_expected = "Hello World,\nhow are you?\nSincerely\nUniverse"
    l3 = ["    ", "\n", ""]

    print("  Testing unicode conversion...")
    assert lines2unicode(l0) == l0_expected
    assert lines2unicode(l1) == l1_expected
    assert lines2unicode(l2) == l2_expected

    assert is_empty(l0)
    assert is_empty(l3)
    assert not is_empty(l1)
    assert not is_empty(l2)

    print("  Testing match...")
    headline = ["     42", " The Meaning of Life and Everything"]
    headline_expected = "42\nThe Meaning of Life and Everything"
    assert match(r"\d+", headline, True)
    assert lines2unicode(headline, True) == headline_expected

    print("  Testing avg word length and avg words per line...")
    l4 = ["x     2  ", "  yz xz"]
    assert avg_word_length(l4) == 1.5

    # avg_words_per_line
    assert avg_words_per_line(l0) == 0.0
    assert avg_words_per_line(l2) == 1.75
    assert avg_words_per_line(l4) == 2.0

    print("Passed all tests!")

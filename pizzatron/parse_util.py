import difflib
import re


def after(s: str, substr: str):
    start = s.find(substr)
    if start == -1:
        return ''
    return s[start + len(substr):]


def normalize(text: str):
    text = text.lower()
    text = re.compile(r'[^\sa-z0-9]').sub('', text)
    text = re.compile(r'\s+').sub(' ', text)
    return text


def tokenize(text: str):
    return [normalize(word) for word in text.split()]


def match_key(key, options):
    if key in options:
        return key

    matches = difflib.get_close_matches(key, options, n=2, cutoff=0.85)
    if len(matches) == 1 and len(matches[0]):
        return matches[0]

    return None


def longest_match_index(options, args):
    current_match = None
    key = ''
    keys = []
    for i, arg in enumerate(args):
        key += arg

        if key in options:
            match = key
        else:
            match = match_key(key, options)
        if match is not None:
            if current_match != match:
                current_match = match
                keys = []
            keys.append(key)

        key += ' '

    if current_match is None:
        return None

    matches = difflib.get_close_matches(current_match, keys, n=1, cutoff=0.85)
    if not matches:
        return None
    match = matches[0]

    return match.count(' ') + 1


def longest_match_index_to_key(index, options, args):
    key = ' '.join(args[:index])
    if key in options:
        return key

    match = match_key(key, options)
    if match is not None:
        return match

    return None


def longest_match_key(options, args):
    index = longest_match_index(options, args)
    if index is None:
        return None

    return longest_match_index_to_key(index, options, args)


def longest_match_value(options, args):
    key = longest_match_key(options, args)
    if key is None:
        return None

    if key in options:
        return options[key]

    return None


def parse_longest_match(options, args, raw_args):
    if not args:
        return None, [], args, [], raw_args

    index = longest_match_index(options, args)
    if index is None:
        return None, [], args, [], raw_args

    left = args[:index]
    right = args[index:]
    raw_left = raw_args[:index]
    raw_right = raw_args[index:]
    name = match_key(' '.join(left), options)
    if name is None:
        return None, [], args, [], raw_args

    result = options[name]

    return result, left, right, raw_left, raw_right

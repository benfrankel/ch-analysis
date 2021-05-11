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


def longest_match(options, args):
    option = None
    key = ''
    keys = []
    for i, arg in enumerate(args):
        key += arg

        if key in options:
            new_option = key
        else:
            new_option = match_key(key, options)

        if new_option is not None:
            if option != new_option:
                option = new_option
                keys = []
            keys.append(key)

        key += ' '

    if option is None:
        return None, None

    best_keys = difflib.get_close_matches(option, keys, n=1, cutoff=0.85)
    if not best_keys:
        return None, None
    best_key = best_keys[0]
    best_index = best_key.count(' ') + 1

    return best_index, option


def parse_longest_match(options, args, raw_args):
    if not args:
        return None, [], args, [], raw_args

    index, key = longest_match(options, args)
    if index is None:
        return None, [], args, [], raw_args
    value = options[key]

    left = args[:index]
    right = args[index:]
    raw_left = raw_args[:index]
    raw_right = raw_args[index:]

    return value, left, right, raw_left, raw_right

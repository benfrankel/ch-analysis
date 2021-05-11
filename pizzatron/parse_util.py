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


def get_match(key, options):
    # Exact match
    if key in options:
        return key

    # Approximate match
    matches = difflib.get_close_matches(key, options, n=2, cutoff=0.85)
    if len(matches) == 1 and len(matches[0]):
        return matches[0]

    # Substring match
    matches = []
    if len(key) >= 3:
        for option in options:
            if key in option and len(option) < 4 * len(key):
                matches.append(option)
        if matches:
            return min(matches, key=len)

    return None


def longest_match(options, args):
    best_option = None
    matching_keys = []
    key = ''
    for i, arg in enumerate(args):
        key += arg

        option = get_match(key, options)
        if option is not None:
            if best_option != option:
                best_option = option
                matching_keys = []
            matching_keys.append(key)

        key += ' '

    if best_option is None:
        return None, None

    best_keys = difflib.get_close_matches(best_option, matching_keys, n=1, cutoff=0.85)
    if best_keys:
        best_key = best_keys[0]
    else:
        best_key = matching_keys[-1]
    best_index = best_key.count(' ') + 1

    return best_index, best_option


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

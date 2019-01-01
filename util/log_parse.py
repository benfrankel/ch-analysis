# Parse verbose logs


# Convert string to type specified by tag
def convert(tag, value):
    if len(value) == 2 and tag.endswith('array'):
        return []

    to_str = lambda e: '' if e == '[null]' else e
    to_bool = lambda e: e == 'true'
    to_int = to_long = int
    to_float = to_double = float

    convert = {
        'utf_string': to_str,
        'bool': to_bool,
        'int': to_int,
        'long': to_int,
        'double': to_float,
    }

    to_array = lambda f: lambda v: [f(e) for e in v[1:-1].split(',')]
    for t, f in convert.items():
        convert[t + '_array'] = to_array(f)

    try:
        return convert[tag](value)
    except KeyError:
        raise ValueError("Unrecognized tag '{}'".format(tag))


# Parse a verbose log line into its indent level, name, and value
def parse_verbose_line(line):
    # Count tabs at start of line
    indent = 0
    while line[indent] == '\t':
        indent += 1

    # Remove leading whitespace from the line (should just strip away tabs)
    line = line.lstrip()

    if line[0] != '(':
        return -1, None, None

    # Split off the tag value between ( and )
    end_tag_index = line.index(')')
    tag, line = line[1:end_tag_index], line[end_tag_index+2:]

    # If there is a : character, this line has a name; otherwise it's just a value. Get the name and value
    delim_index = line.find(':')
    if delim_index == -1:
        name, value = '', line
    else:
        name, value = line[:delim_index], line[delim_index+2:]

    # Create the corresponding object from tag, name, and value
    if tag == 'sfs_array':
        return indent, name, []
    elif tag == 'sfs_object':
        return indent, name, {}

    return indent, name, convert(tag, value)


def parse_verbose(raw):
    # List of parsed extension responses
    extensions = []

    # Keep track of the current object or array being constructed
    layer_stack = []
    for line in raw.splitlines():
        # Ignore whitespace and empty lines
        if not line or line.isspace():
            continue

        # If this is a new extension, append it to the list and set it as the current layer
        if 'Received extension response:' in line:
            name = line.split(': ')[1]
            extensions.append({'_FROM': 'server', '_NAME': name})
            layer_stack = [extensions[-1]]
        elif 'Sending zone extension request:' in line:
            name = line.split(': ')[1]
            extensions.append({'_FROM': 'client', '_NAME': name})
            layer_stack = [extensions[-1]]

        # Parse current line
        indent, name, line_obj = parse_verbose_line(line)

        # If this line is invalid, ignore it
        if indent == -1:
            continue

        # Adjust to an older layer if this line de-indented
        layer_stack = layer_stack[:indent]

        # Add the line's object to the growing structure
        if isinstance(layer_stack[-1], list):
            layer_stack[-1].append(line_obj)
        else:
            layer_stack[-1][name] = line_obj

        if isinstance(line_obj, list) or isinstance(line_obj, dict):
            layer_stack.append(line_obj)

    return extensions


def parse_battle_log(raw):
    messages = []

    def convert(val):
        try:
            return int(val)
        except ValueError:
            pass

        try:
            return float(val)
        except ValueError:
            pass

        if len(val) != 0 and val[0] + val[-1] in ('()', '[]', '{}'):
            return [convert(x) for x in val[1:-1].split(', ')]
        if '|' in val:
            return val.split('|')

        return val

    for line in raw.splitlines():
        # Ignore non-message lines
        if not line.startswith('BATTLE LOG: '):
            words = line.split()
            if len(words) == 3:
                event, player_index, remaining = words
                if event == 'startTimer' or event == 'stopTimer':
                    player_index = int(player_index)
                    remaining = int(remaining)
                    messages.append({'Event': event, 'PlayerIndex': player_index, 'Remaining': remaining})
            continue

        line = line[12:]

        values = []
        names = []
        parsing_value = True
        end_index = len(line)

        for i, c in enumerate(line[::-1]):
            index = len(line) - i - 1
            if parsing_value:
                if c == '=':
                    if line[index-1] != ' ':
                        values.append(convert(line[index+1:end_index]))
                        end_index = index
                        parsing_value = False
            elif c == ',':
                names.append(line[index+1:end_index])
                end_index = index
                parsing_value = True

        params = dict()
        for i, name in enumerate(names):
            params[name] = values[i]

        messages.append(params)

    return messages


def parse_battle(raw):
    # TODO: Crop raw to just battle start and end?
    return parse_verbose(raw), parse_battle_log(raw)

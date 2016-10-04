# This file parses verbose battle logs and battle log messages.

# List of tags that may appear.
basic_tags = 'utf_string', 'utf_string_array', 'bool', 'bool_array', 'int', 'int_array', 'double', 'double_array'
struct_tags = 'sfs_array', 'sfs_object'


# A primitive type, as in, any type from basic_tags. It has a tag (type), a name, and a value.
class SFSBasicType:
    def __init__(self, tag, name, value):
        self.tag = tag
        self.name = name
        self.value = None

        # If possible, convert the string value into the proper type as dictated by tag.
        try:
            if self.tag == 'utf_string':
                self.value = value
            elif self.tag == 'utf_string_array':
                self.value = value[1:-1].split(',')
            elif self.tag == 'bool':
                self.value = value == 'true'
            elif self.tag == 'bool_array':
                self.value = [e == 'true' for e in value[1:-1].split(',')]
            elif self.tag == 'int':
                self.value = int(value)
            elif self.tag == 'int_array':
                self.value = [int(e) for e in value[1:-1].split(',')]
            elif self.tag == 'double':
                self.value = [float(value)]
            elif self.tag == 'double_array':
                self.value = [float(e) for e in value[1:-1].split(',')]
        except ValueError:
            pass

    def __eq__(self, other):
        return self.tag == other.tag and self.name == other.name and self.value == other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return '%s(%s, %s, %s)' % (self.__class__.__name__, self.tag, self.name, self.value)


# An (sfs_array). Behaves identically to an array but also has .name and .tag attributes.
class SFSArray:
    def __init__(self, name):
        self.tag = 'sfs_array'
        self.name = name
        self.array = list()

    def add_item(self, item):
        if item.tag in basic_tags:
            self.array.append(item.value)
        else:
            self.array.append(item)

    def __eq__(self, other):
        return self.tag == other.tag and self.name == other.name and self.array == other.array

    def __contains__(self, *args, **kwargs):
        return self.array.__contains__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        self.array.__delitem__(*args, **kwargs)

    def __getitem__(self, y):
        return self.array.__getitem__(y)

    def __iter__(self, *args, **kwargs):
        return self.array.__iter__()

    def __len__(self, *args, **kwargs):
        return self.array.__len__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        return self.array.__setitem__(*args, **kwargs)

    def __str__(self):
        return self.array.__str__()

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.name, self.array)


# An (sfs_object). Behaves identically to a dictionary but also has .name and .tag attributes.
class SFSObject:
    def __init__(self, name):
        self.tag = 'sfs_object'
        self.name = name
        self.attr = dict()

    def add_item(self, item):
        if item.tag in basic_tags:
            self.attr[item.name] = item.value
        else:
            self.attr[item.name] = item

    def __eq__(self, other):
        return self.tag == other.tag and self.name == other.name and self.attr == other.attr

    def __contains__(self, *args, **kwargs):
        return self.attr.__contains__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        self.attr.__delitem__(*args, **kwargs)

    def __getitem__(self, y):
        return self.attr.__getitem__(y)

    def __iter__(self, *args, **kwargs):
        return self.attr.__iter__()

    def __len__(self, *args, **kwargs):
        return self.attr.__len__()

    def __setitem__(self, *args, **kwargs):
        self.attr.__setitem__(*args, **kwargs)

    def __str__(self):
        return self.attr.__str__()

    def __repr__(self):
        return '<%s %s%s>' % (self.__class__.__name__, self.name, self.attr)


# Input is a single line, output is the indent level along with the object created from the line.
def parse_verbose_line(line):
    # Count tabs at start of line.
    indent = 0
    while line[indent] == '\t':
        indent += 1

    # Remove leading whitespace from the line (should just strip away tabs).
    line = line.lstrip()

    # Split off the tag value between ( and ).
    end_tag_index = line.index(')')
    tag, line = line[1:end_tag_index], line[end_tag_index+2:]

    # If there is a : character, then this line has a name, otherwise it's just a value. Get the name and value.
    delim_index = line.find(':')
    if delim_index == -1:
        name, value = '', line
    else:
        name, value = line[:delim_index], line[delim_index+2:]

    # Create the appropriate object from tag, name, and value.
    if tag in basic_tags:
        result = SFSBasicType(tag, name, value)
    elif tag == 'sfs_array':
        result = SFSArray(name)
    else:  # tag == 'sfs_object'
        result = SFSObject(name)

    return indent, result


def parse_verbose(raw):
    # List of parsed extension responses so far.
    extension_responses = []

    # Keep track of the current object or array that we're constructing.
    layer_stack = []
    for line in raw.splitlines():
        # Ignore whitespace and empty lines.
        if not line or line.isspace():
            continue

        # If this is a new extension response, append it to the list and set it as the current layer.
        if 'Received extension response:' in line:
            extension_responses.append(SFSObject(line.split(': ')[1]))
            layer_stack = [extension_responses[-1]]

        # If this line is invalid, ignore it.
        if line[0] != '\t' or ')' not in line:
            if extension_responses and extension_responses[-1].name == 'battleResults':
                break
            continue

        # Parse the current line.
        indent, line_obj = parse_verbose_line(line)

        # Adjust to the proper layer, if this line de-indented.
        layer_stack = layer_stack[:indent]

        # Add the line's object to the growing structure.
        layer_stack[-1].add_item(line_obj)
        if line_obj.tag in struct_tags:
            layer_stack.append(line_obj)

    return extension_responses


def parse_messages(raw):
    # List of messages so far.
    messages = []

    def convert(val):
        try:
            return int(val)
        except ValueError:
            try:
                return float(val)
            except ValueError:
                if len(val) != 0 and val[0] + val[-1] in ('()', '[]', '{}'):
                    return [convert(x) for x in val[1:-1].split(', ')]
                if '|' in val:
                    return val.split('|')
                if ',' in val and '=' not in val:
                    return val.split(',')
                return val

    for line in raw.splitlines():
        # Ignore non-message lines.
        if 'BATTLE LOG: ' not in line:
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
    return parse_verbose(raw), parse_messages(raw)

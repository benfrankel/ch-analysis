# This file parses verbose battle logs.

basic_tags = 'utf_string', 'utf_string_array', 'bool', 'int', 'int_array'
struct_tags = 'sfs_array', 'sfs_object'


class SFSBasicType:
    def __init__(self, tag, name, value):
        self.tag = tag
        self.name = name
        self.value = None
        if self.tag == 'utf_string':
            self.value = value
        elif self.tag == 'utf_string_array':
            if value[0] == '[' and value[-1] == ']':
                self.value = value[1:-1].split(',')
        elif self.tag == 'bool':
            if value in ('true', 'false'):
                self.value = value == 'true'
        elif self.tag == 'int':
            if value.isdigit():
                self.value = int(value)
        elif self.tag == 'int_array':
            if value[0] == '[' and value[-1] == ']':
                values = value[1:-1].split(',')
                if all(e.isdigit() for e in values):
                    self.value = [int(e) for e in values]

    def __eq__(self, other):
        return self.tag == other.tag and self.name == other.name and self.value == other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return '%s(%s, %s, %s)' % (self.__class__.__name__, self.tag, self.name, self.value)


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


def parse_line(line):
    indent = 0
    while line[indent] == '\t':
        indent += 1
    line = line.strip()
    end_tag_index = line.index(')')
    tag, line = line[1:end_tag_index], line[end_tag_index+2:]
    delim_index = line.find(':')
    if delim_index == -1:
        name, value = '', line
    else:
        name, value = line[:delim_index], line[delim_index+2:]
    if tag in basic_tags:
        result = SFSBasicType(tag, name, value)
    elif tag == 'sfs_array':
        result = SFSArray(name)
    else:  # tag == 'sfs_object'
        result = SFSObject(name)
    return indent, result


def parse_battle(raw):
    extension_responses = []
    layer_stack = []
    for line in raw.splitlines():
        if not line or line.isspace():
            continue
        if 'Received extension response:' in line:
            extension_responses.append(SFSObject(line.split(': ')[1]))
            layer_stack = [extension_responses[-1]]
        if line[0] != '\t':
            if extension_responses and extension_responses[-1].name == 'battleResults':
                break
            continue
        indent, line_obj = parse_line(line)
        layer_stack = layer_stack[:indent]
        layer_stack[-1].add_item(line_obj)
        if line_obj.tag in struct_tags:
            layer_stack.append(line_obj)
    return extension_responses


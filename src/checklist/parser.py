from hashlib import md5
import json
import os

__all__ = ['content_to_tree']


class Node(object):
    def __init__(self, content):
        self.parent = None
        self.childs = []
        self.depth = 0
        self.content = content

    def add_child(self, node):
        self.childs.append(node)
        node._set_parent(self)

    def _set_parent(self, node):
        self.depth = node.depth + 1
        self.parent = node

    def __repr__(self):
        result = ' '*(self.depth * 4) + repr(self.content) + '\n'
        for child in self.childs:
            result += repr(child)
        return result


class NodeContent(object):
    def __init__(self, name):
        self.name = name
        self.id = ''

    def __repr__(self):
        result = self.name
        if self.id:
            result += ' <{0}>'.format(self.id)
        result += ':'
        return result


class RootContent(NodeContent):
    def __init__(self):
        super(RootContent, self).__init__('root')
        self.id = '__root'


class TextContent(NodeContent):
    def __init__(self, name, text):
        super(TextContent, self).__init__(name)
        self.text = text
        self.ifs = []
        self.if_nots = []
        self.id = md5(self.text).hexdigest()
        self.help_type = None
        self.help_content = None

    def __repr__(self):
        result = super(TextContent, self).__repr__()
        result += ' ' + self.text
        if self.ifs:
            result += ' (if: {0})'.format(', '.join(self.ifs))
        if self.if_nots:
            result += ' (ifnot: {0})'.format(', '.join(self.if_nots))
        return result


class ConditionalContent(TextContent):
    def __init__(self, text, on=False):
        super(ConditionalContent, self).__init__('conditional', text)
        self.on = on

    def __repr__(self):
        result = super(ConditionalContent, self).__repr__()
        result += ' (on: {0})'.format(self.on)
        return result


class Parser(object):
    def __init__(self):
        self.current_ifs = []
        self.current_if_nots = []
        self.ifs_order = []

    def get_node_content(self, string, depth):
        loaded_json = json.loads(string)
        if isinstance(loaded_json, basestring):
            text = loaded_json
            if depth == 1:
                node_content = TextContent('section_title', text)
            else:
                node_content = TextContent('checkbox', text)
        elif isinstance(loaded_json, dict):
            options_dict = loaded_json
            text = options_dict['text']
            if 'type' not in options_dict:
                node_content = TextContent('checkbox', text)
            elif options_dict['type'] == 'conditional':
                default = options_dict.get('default')
                if default not in ('yes', 'no', None):
                    raise_bad_value_message('default', default)
                node_content = ConditionalContent(text, default == 'yes')
            else:
                raise_bad_value_message('type', options_dict['type'])

            # This if
            if 'if' in options_dict:
                ifs = options_dict['if']
                if isinstance(ifs, basestring):
                    node_content.ifs.append(ifs)
                elif isinstance(ifs, list):
                    node_content.ifs.extend(ifs)
                else:
                    raise_bad_value_message('if', ifs)
            if 'ifnot' in options_dict:
                if_nots = options_dict['ifnot']
                if isinstance(if_nots, basestring):
                    node_content.if_nots.append(if_nots)
                elif isinstance(if_nots, list):
                    node_content.if_nots.extend(if_nots)
            if 'id' in options_dict:
                assert isinstance(options_dict['id'], basestring)
                node_content.id = options_dict['id']
            if 'help_type' in options_dict:
                help_type = options_dict['help_type']
                assert isinstance(help_type, basestring)
                assert help_type in ['tooltip', 'link']
                if help_type == 'tooltip':
                    help_content = get_help_text(node_content.id)
                elif help_type == 'link':
                    help_content = options_dict['help_link']
                assert isinstance(help_content, basestring)
                node_content.help_type = help_type
                node_content.help_content = help_content
            else:
                help_content = get_help_text(node_content.id)
                if isinstance(help_content, basestring):
                    node_content.help_type = 'tooltip'
                    node_content.help_content = help_content
        else:
            assert False, 'JSON type not supported ({0}): {1}'.format(type(loaded_json).__name__, string)
        node_content.ifs.extend(self.current_ifs)
        node_content.if_nots.extend(self.current_if_nots)
        return node_content

    def content_to_tree(self, content):
        root = Node(RootContent())
        last_node = root
        for line in content.splitlines():
            stripped_line = line.strip()
            if not stripped_line:
                continue
            current_spaces = count_left_spaces(line)
            assert current_spaces % 4 == 0
            depth = current_spaces // 4 + 1
            assert 1 <= depth <= last_node.depth + 1
            if stripped_line.startswith('%'):
                self.handle_command(stripped_line, depth)
            else:
                node = Node(self.get_node_content(stripped_line, depth))
                parent_node = last_node
                while depth < parent_node.depth + 1:
                    parent_node = parent_node.parent
                parent_node.add_child(node)
                last_node = node
        assert len(self.current_ifs) == 0
        assert len(self.current_if_nots) == 0
        assert len(self.ifs_order) == 0
        return root

    def handle_command(self, string, depth):
        tokens = string[1:].split()
        command, args = tokens[0], tokens[1:]
        args = [json.loads(arg) for arg in args]
        if command == 'if':
            assert len(args) == 1
            assert isinstance(args[0], basestring)
            self.current_ifs.append(args[0])
            self.ifs_order.append(command)
        elif command == 'ifnot':
            assert len(args) == 1
            assert isinstance(args[0], basestring)
            self.current_if_nots.append(args[0])
            self.ifs_order.append(command)
        elif command == 'endif':
            assert len(args) == 0
            last_if_command = self.ifs_order.pop()
            if last_if_command == 'if':
                self.current_ifs.pop()
            elif last_if_command == 'ifnot':
                self.current_if_nots.pop()
            else:
                assert False
        else:
            raise_bad_value_message('% command', command)


def content_to_tree(content):
    return Parser().content_to_tree(content)


# HELPER FUNCTIONS

def count_left_spaces(string):
    count = 0
    for c in string:
        if c == ' ':
            count += 1
        else:
            break
    return count


def raise_bad_value_message(key, value):
    assert False, 'Unknown value for "{0}": {1}'.format(key, value)


def get_help_text(node_id):
    help_file = os.path.join(os.path.dirname(__file__), 'structure', 'help', node_id)
    try:
        with open(help_file) as f:
            help_text = f.read()
    except IOError:
        return None
    return html_escape(help_text)


def html_escape(html):
    """
    Returns the given HTML with ampersands, quotes and angle brackets encoded.
    """
    return html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

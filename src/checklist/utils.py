"""
Checklist utilities module
"""
import os

from .parser import content_to_tree
from .tree2html import tree_to_html

__all__ = ['generate_checklist']


def generate_checklist():
    root_folder = os.path.join(os.path.dirname(__file__), 'structure')
    with open(os.path.join(root_folder, 'format.json')) as f:
        content = f.read()
    root = content_to_tree(content)
    html_output = tree_to_html(root)
    return html_output

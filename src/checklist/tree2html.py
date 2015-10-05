__all__ = ['tree_to_html']


def print_root(root):
    return ''


def print_section_title(section_title_node):
    return '<h3 class="section_title">{0}</h3>'.format(section_title_node.text)


def print_checkbox(
        checkbox_node,
        checked=False,
        checkbox_classes='',
        label_classes='',
        ):
    checked_attribute = 'checked="yes"' if checked else ''
    result = ('<input id="{0}" type="checkbox" {1} class="{4}"/>'
        '<label for="{0}" class="checkbox_text {2}">{3}</label>').format(
        checkbox_node.id,
        checked_attribute,
        label_classes,
        checkbox_node.text,
        checkbox_classes
        )
    if checkbox_node.help_type == 'tooltip':
        result += ('<span class="help_icon tooltip_help" title="{0}">?</span>'
                .format(checkbox_node.help_content))
    elif checkbox_node.help_type == 'link':
        result += ('<a class="help_icon link_help" href="{0}">?</a>'
                .format(checkbox_node.help_content))
    ifs_ids = ','.join('#' + _id for _id in checkbox_node.ifs)
    if_nots_ids = ','.join('#' + _id for _id in checkbox_node.if_nots)
    result += """
<script>
$(function() {{
    function handle_ifs_change() {{
        if ($('{1}').not(':checked').length + $('{2}').filter(':checked').length == 0) {{
            $('#{0}').parent().show();
        }} else {{
            $('#{0}').parent().hide();
        }}
    }}
    $('{1}').change(handle_ifs_change);
    $('{2}').change(handle_ifs_change);
    handle_ifs_change();
}});
</script>
""".format(checkbox_node.id, ifs_ids, if_nots_ids)
    return result


def print_conditional(conditional_node):
    return print_checkbox(
            conditional_node,
            conditional_node.on,
            'hidden',
            'conditional',
            )


def tree_to_html(node):
    node_output = '<div>'
    node_output += '<span class="indent"></span>'*(node.depth - 2)
    node_output += globals()['print_' + node.content.name](node.content)
    node_output += '</div>'
    for child in node.childs:
        node_output += tree_to_html(child)
    return node_output

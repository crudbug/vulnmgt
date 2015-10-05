Ink.requireModules(
            ['Ink.UI.ExtendedIssuesDBTable_1',
            'Ink.Util.String_1',
            'Ink.Dom.Element_1',
            'Ink.Dom.Event_1'],
            function(ExtendedIssuesDBTable,
              InkString,
              Element,
              Event) {
    ExtendedIssuesDBTable.prototype._trFromItem = function(item, fields)    {
        var tr_el = document.createElement('tr');
        var td_el = Element.create('td');
        td_el.innerHTML = '<input class="actions-select-single" type="checkbox" value="' + item.id + '">';
        tr_el.appendChild(td_el);

        var tr_classes = item['classes'] || {};
        for (j = 0; j < fields.length; j++) {
            var field = fields[j];
            var value = item[field];
            if (item[field] !== null && typeof item[field] === 'object' && 'name' in item[field]) {
                value = item[field].name;
            }
            var td_classes = tr_classes[field] || '';

            td_el = Element.create('td', {'class': 'col_' + field + ' ' + td_classes});

            var td_content;
            if ('project' in item) {
                td_content = '<a class="default-anchor" href="/issue/?project=' + item.project.id + '&audit=' + item.id +  '">';
            } else {
                td_content = '<a class="default-anchor" href="/issue/?project=' + item.id +  '">';
            }
            td_content += '<p>';
            if (field == 'finished') {
                if (value == 'true') {
                    value = 'Yes';
                }
                else {
                    value = 'No';
                }
            }
            td_content += InkString.htmlEscapeUnsafe(value) || '';
            td_content += '</p>';
            td_content += '</a>';

            td_el.innerHTML = td_content;
            tr_el.appendChild(td_el);
        }
        td_el = Element.create('td');
        td_el.innerHTML = '<a href="/project_report/' + item.id + '"><span class="icon-globe"></span></a>';
        tr_el.appendChild(td_el);

        td_el = Element.create('td');
        td_el.innerHTML = '<a href="/project_report_pdf/' + item.id + '"><span class="icon-file-text"></span></a>';
        tr_el.appendChild(td_el);

        td_el = Element.create('td');
        td_el.innerHTML = '<a href="' + item.id + '"><span class="icon-pencil"></span></a>';
        tr_el.appendChild(td_el);
        return tr_el;
    };
});

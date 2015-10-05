Ink.requireModules(
            ['Ink.UI.ExtendedIssuesDBTable_1',
            'Ink.Util.String_1',
            'Ink.Dom.Event_1',
            'Ink.Dom.Element_1',
            'Ink.Dom.Selector_1'],
            function(ExtendedIssuesDBTable,
              InkString,
              Event,
              Element,
              Selector) {
    ExtendedIssuesDBTable.prototype._trFromItem = function(item, fields)    {
        fields.push("edit_report");
        fields.push("download_report_pdf");

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
            if (value === true) {
                value = 'Yes';
            }
            else if (value === false) {
                value = 'No';
            }
            var td_classes = tr_classes[field] || '';

            td_el = Element.create('td', {'class': 'col_' + field + ' ' + td_classes});

            var td_content = '';
            if (field === "edit_report") {
                td_content = '<a href="/reportconfig/' + item.id + '"><span class="icon-pencil"></span></a>';
            } else if (field === "download_report_pdf") {
                td_content = '<a href="/download_report_pdf/' + item.id + '" title="Download as PDF"><span class="icon-file-text"></span></a>';
            } else {
                td_content = '<a class="default-anchor" href=/view_report/' + item.id + '>';
                td_content += '<p>';
                td_content += InkString.htmlEscapeUnsafe(value) || '';
                td_content += '</p>';
                td_content += '</a>';
            }
            td_el.innerHTML = td_content;
            tr_el.appendChild(td_el);
        }
        fields.pop();
        fields.pop();
        return tr_el;
    };
});


Ink.requireModules(['Ink.UI.ExtendedIssuesDBTable_1'], function(ExtendedIssuesDBTable) {
    // Actions
    var changelist_table = new ExtendedIssuesDBTable('#changelist', {
        paginationOptions: {
            maxSize: 5,
            firstLabel:        'First',
            lastLabel:         'Last',
            previousPageLabel: '<span class="icon-chevron-left"></span><span class="icon-chevron-left"></span>',
            nextPageLabel:     '<span class="icon-chevron-right"></span><span class="icon-chevron-right"></span>',
            previousLabel:     '<span class="icon-chevron-left"></span> Previous',
            nextLabel:         'Next <span class="icon-chevron-right"></span>'
        },
        extraFilters: {
          '#id_project': 'project',
          '#id_audit': 'audit',
        }
    });

});

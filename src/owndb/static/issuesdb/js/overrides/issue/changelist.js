jQuery(function ($) {
Ink.requireModules(
            [
            'Ink.Dom.Selector_1',
            'Ink.Dom.Loaded_1',
            'Ink.Dom.Css_1',
            'Ink.Dom.Event_1',
            'Ink.Dom.Element_1',
            'Ink.Util.Array_1',
            'Ink.UI.ExtendedIssuesDBTable_1',
            'Ink.UI.Tooltip_1',
            'Ink.Util.String_1'],
            function(
              Selector,
              Loaded,
              Css,
              Event,
              Element,
              InkArray,
              ExtendedIssuesDBTable,
              Tooltip,
              InkString) {

    ExtendedIssuesDBTable.prototype._trFromItem = function(item, fields)    {
        var tr_el = document.createElement('tr');
        var td_el = Element.create('td');
        td_el.innerHTML = '<input class="actions-select-single" type="checkbox" value="' + item.id + '">';
        tr_el.appendChild(td_el);

        //td_el = Element.create('td');
        //td_el.innerHTML = '<a href="' + item.id + '"><span class="fa-pencil-square"></span></a>';
        //tr_el.appendChild(td_el);

        for (j = 0; j < fields.length; j++) {
            var field = fields[j];

            if (field !== 'severity') {
                td_el = Element.create('td', {'class': 'col_' + field});
            }
            else {
                td_el = Element.create('td', {'class': 'col_' + field + ' severity-' + item[field].name.toLowerCase().replace(' ', '-', 'g')});
            }

            var td_content = '';
            if (field == 'information') {
              new Tooltip(td_el, {
                html: item[field],
                where: 'left'
              });

              if (item[field] !== '') {
                td_content = '<span class="icon-question-sign"></span>';
              }
            }
            else if (field == 'avoc_state') {
              td_content = item[field].name;
              var html = '';
              if (item['avoc_scan_date']) {
                  html =  ' [' + item['avoc_scan_date'] + ']'
              }
              new Tooltip(td_el, {
                html: item['avoc_state_msg'] + html,
                where: 'left'
              });

              //if (item[field] == 'vulnerable') {
              //  td_content = '<span class="icon-check-empty"></span>';
              //}
              //else if (item[field] == 'not vulnerable') {
              //  td_content = '<span class="icon-check"></span>';
              //}
              //else if (item[field] !== '') {
              //  td_content = '<span class="icon-exclamation"></span>';
              //}
            }
            else {
              td_content = '<p>';
              var value = item[field];
              if (item[field] !== null && typeof item[field] === 'object' && 'name' in item[field]) {
                value = item[field].name;
              }
              td_content += InkString.htmlEscapeUnsafe(value) || '';
              td_content += '</p>';
              if (field == 'project') {
                td_content = '<a href="/issue/?project=' + item.project.id +  '">' + td_content;
              }
              else if (field == 'audit' && item[field] !== null) {
                td_content = '<a href="/issue/?project=' + item.project.id + '&audit=' + item.audit.id +  '">' + td_content;
              }
              else {
                td_content = '<a class="default-anchor" href="/issue/' + item.id +  '">' + td_content;
              }
              td_content += '</a>';
            }

            td_el.innerHTML = td_content;
            tr_el.appendChild(td_el);
        }
        return tr_el;
    };

    var projectFilter = Element.get('id_project');
    var auditFilter = Element.get('id_audit');
    var originalHref = null;
    function handleAuditChange() {
        var currentProject = projectFilter.value;
        var currentAudit = auditFilter.value;
        InkArray.each(Selector.select('.prepare-report-button'), function(reportButton) {
            if (originalHref === null) {
                originalHref = reportButton.href;
            }
            reportButton.href = originalHref + '?';
            reportButton.href += 'project=' + currentProject;
            reportButton.href += '&audit=' + currentAudit;
        });
    }
    $(projectFilter).change('change', handleAuditChange);
    $(auditFilter).change('change', handleAuditChange);
    handleAuditChange();
});
});

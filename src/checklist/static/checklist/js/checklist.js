$(function() {
    $('#save_button').click(function() {
        var state = '';
        $('input[type="checkbox"]').each(function(i, e) {
            state += e.id + ' ' + $(e).is(':checked') + '\n';
        });
        $('#checklist_state_area').val(state);
    });
    $('#load_button').click(function() {
        var state = $('#checklist_state_area').val();
        var lines = state.split("\n");
        $.each(lines, function(n, line) {
            line = $.trim(line);
            if (line) {
                var tokens = line.split(" ");
                var elem_id = tokens[0];
                var checked = tokens[1] == 'true';
                $('#' + elem_id).attr('checked', checked);
                $('#' + elem_id).change();
            }
        });
    });
});

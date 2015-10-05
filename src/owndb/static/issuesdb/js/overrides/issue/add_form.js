jQuery(function ($) {
Ink.requireModules(
            [
            'Ink.Dom.Selector_1',
            'Ink.Util.Array_1',
            'Ink.Dom.Event_1',
            'Ink.Util.Date_1'
            ],
            function(
              Selector,
              InkArray,
              Event,
              InkDate) {
    //
    var add_audit_el = Selector.select('#add_audit')[0],
      original_href = add_audit_el.href,
      project_selector = Selector.select('#id_project')[0];
    add_audit_el.href = original_href + '&project=' + project_selector.value;
    $(project_selector).change(function(evt) {
      add_audit_el.href = original_href + '&project=' + project_selector.value;
    });

    var state_select_el = Selector.select('#id_state')[0];
    Event.observe(state_select_el, 'change', function(event) {
      var date_el;
      var date_value = InkDate.get();
      if (state_select_el.value == '10R') {
        date_el = Selector.select('#id_report_date')[0];
        if (date_el.value === '') {
          date_el.value = date_value;
        }
      }
      else if (state_select_el.value == '20F' || state_select_el.value == '30I') {
        date_el = Selector.select('#id_report_date')[0];
        if (date_el.value === '') {
          date_el.value = date_value;
        }
        date_el = Selector.select('#id_fix_date')[0];
        if (date_el.value === '') {
          date_el.value = date_value;
        }
      }
    });

    InkArray.each(Selector.select('.yesterday'), function(yesterday_button) {
      var last_index = yesterday_button.id.lastIndexOf('_');
      var date_field_id = yesterday_button.id.substring(0, last_index);
      Event.observe(yesterday_button, 'click', function(){
        var date = new Date();
        date.setDate(date.getDate()-1);
        Selector.select('#' + date_field_id)[0].value = InkDate.get('Y-m-d', date);
      });
    });

});
});

Ink.requireModules(
            ['Ink.Dom.Selector_1',
            'Ink.Dom.Event_1',
            'Ink.Util.Date_1'
            ],
            function(Selector,
              Event,
              InkDate) {
    var state_select_el = Selector.select('#id_finished')[0];
    Event.observe(state_select_el, 'click', function(event) {
      var date_el;
      date_el = Selector.select('#id_end_date')[0];
      if (event.target.checked) {
        var date_value = InkDate.get();
        date_el.value = date_value;
      }
      else {
        date_el.value = '';
      }
    });
});

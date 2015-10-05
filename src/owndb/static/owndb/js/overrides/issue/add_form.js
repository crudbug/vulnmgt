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

  // TODO being used?
  var full_payload_el = Selector.select('#id_full_payload')[0],
    location_el = Selector.select('#id_location')[0],
    method_el = Selector.select('#id_method')[0];

  var option, method_dict = {};
  for (option in method_el.options) {
    method_dict[method_el.options[option].innerHTML] = option;
  }

  Event.observe(full_payload_el, 'change', function(evt) {
    var re = /(GET|POST|TRACE|OPTIONS|PUT|DELETE)\s+(.+?)\s*(?:HTTP\/\d\.\d)?\s*$/m
    var re_host = /Host:\s+(.+?)\s*$/m
    var values = re.exec(full_payload_el.value);
    var host = re_host.exec(full_payload_el.value)
    if (values && host) {
      if (method_el.value === '') method_el.value = method_dict[values[1]];
      if (location_el.value === '') location_el.value = 'http://' + host[1] + values[2];
    }
  });

});

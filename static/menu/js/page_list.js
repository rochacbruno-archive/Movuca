$(document).ready(function () {

   var availableTags = ["banana"];

   $.getJSON('../tagcloud.json', function(data) {
      $.each(data['tags'], function(key, val) {
        availableTags.push(key);
      });

      $('#internal_page_tags').tagit({
       removeConfirmation: true,
       availableTags: availableTags,
       });
   });

   if ($('.tagit').length == 0) {
      $('#internal_page_tags').tagit({
       removeConfirmation: true,
      });
   }

});

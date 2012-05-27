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

  var formObject = $('#internal_page_form');
  formObject.data('original_serialized_form', formObject.serialize());
 
  $(':submit').click(function() {
    window.onbeforeunload = null;
  });
 
  window.onbeforeunload = function() {
    if (formObject.data('original_serialized_form') !== formObject.serialize()) {
      return "If you leave the page all your changes will be lost!.";
    }
  };

});

$(function(){
  var formObject = $('#internal_page_form');
  formObject.data('original_serialized_form', formObject.serialize());
 
  $(':submit').click(function() {
    window.onbeforeunload = null;
  });
 
  window.onbeforeunload = function() {
    if (formObject.data('original_serialized_form') !== formObject.serialize()) {
      return "If you leave the page all your changes will be lost!.";
    }
  };
});


function check_check(obj){
    if ($(obj).is(':checked')){
           $('#publish').hide();
           $('#draft').show();
       }else{
           $('#draft').hide();
           $('#publish').show();
       }
}

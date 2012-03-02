$(document).ready(function () {

   check_check($('#article_draft'));
   

   $('#article_draft').change(function(){
      check_check($(this));
   });

   var availableTags = ["banana"];

   $.getJSON('../tagcloud.json', function(data) {
      $.each(data['tags'], function(key, val) {
        availableTags.push(key);
      });

      $('#article_tags').tagit({
       removeConfirmation: true,
       availableTags: availableTags,
       });
   });

   if ($('.tagit').length == 0) {
      $('#article_tags').tagit({
       removeConfirmation: true,
      });
   }

   var formObject = $('#article_form');
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
  var formObject = $('#article_form');
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

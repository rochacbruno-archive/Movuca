$(document).ready(function () {

   check_check($('#article_draft'));
   

   $('#article_draft').change(function(){
      check_check($(this));
   });

   $('#article_tags').tagit({removeConfirmation: true});



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
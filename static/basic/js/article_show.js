$(document).ready(function () {
  $(".related-articles li").click(function(){
     window.location = $(this).attr("data-url");
  });
});
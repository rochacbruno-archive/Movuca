$(document).ready(function () {
  $(".list-article-wrapper").click(function(){
     window.location = $(this).attr("data-url");
  });

  $('.carousel').carousel();

  $('.memberpicture').popover({"placement": "top"});
  $('.captioned').popover({"placement": "left"});

});
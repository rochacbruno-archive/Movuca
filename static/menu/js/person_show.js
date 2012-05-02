$(document).ready(function () {

	 $('.carousel').carousel();
	 
  $(".list-article-wrapper").click(function(){
     window.location = $(this).attr("data-url");
  });
});
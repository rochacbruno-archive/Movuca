$(document).ready(function () {
  $(".related-articles li").click(function(){
     window.location = $(this).attr("data-url");
  });


  var loadPhoto=function(hash){ 
                           var w = $(window).width()
                           var h = $(window).height()
                           hash.w.children("img").attr('src', hash.t.src).css({'max-width':w - 100, 'max-height': h - 100})
                           hash.w.css(
                                     {
                                     'width':'auto',
                                     'max-width':w - 100,
                                     'max-height': h - 100,
                                     'top': '5%',
                                     'left': '40%',

                                      }
                                      ).show();
                            
                         }; 
  $('#photomodal').jqm({modal: false, 
                        trigger: '.show-article-content img, .commentitem img',
                        onShow:loadPhoto});
});
$(document).ready(function () {
  $(".related-articles li").click(function(){
     window.location = $(this).attr("data-url");
  });

  //$('#photomodal').jqm({ajax: $('img.recipephoto').attr('src'),modal: true, trigger: 'img.recipephoto'});
  //$('#photomodal').jqm({ajax: '@src', target: '.photo',modal: true, trigger: 'img.recipephoto'});
  //var myOpen=function(hash){ hash.w.css('background','red').show(); };
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
                        trigger: 'img.recipephoto, .commentitem img, .cook-recipe-instructions img',
                        onShow:loadPhoto});
});
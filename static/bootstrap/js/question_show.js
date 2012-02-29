$(document).ready(function () {
  $(".related-articles li").click(function(){
     window.location = $(this).attr("data-url");
  });

    $(".vote").click(function(){
        url = $(this).attr('data-url');
        ajax(url,[],':eval');
    });

  $(".remove-reply").click(function(){
    if (confirm("delete?")) {
        url = $(this).attr('data-url');
        ajax(url,[1],'');
        $(this).parent().hide();
    }
  });
   
  // var loadPhoto=function(hash){ 
  //                          var w = $(window).width()
  //                          var h = $(window).height()
  //                          hash.w.children("img").attr('src', hash.t.src).css({'max-width':w - 100, 'max-height': h - 100})
  //                          hash.w.css(
  //                                    {
  //                                    'width':'auto',
  //                                    'max-width':w - 100,
  //                                    'max-height': h - 100,
  //                                    'top': '5%',
  //                                    'left': '40%',

  //                                     }
  //                                     ).show();
                            
  //                        }; 
  // $('#photomodal').jqm({modal: false, 
  //                       trigger: '.show-article-content img, .commentitem img',
  //                       onShow:loadPhoto});
});


function removereply(selector) {
          if (confirm("delete?")) {
              obj = jQuery('#' + selector);
              url = obj.attr("data-url");
              ajax(url+selector,[1],'');
              obj.hide();
              return false;
              }
      }

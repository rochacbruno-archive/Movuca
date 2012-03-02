$(document).ready(function () {
  $(".related-articles li").click(function(){
     window.location = $(this).attr("data-url");
  });

    $(".vote").click(function(){
        url = $(this).attr('data-url');
        ajax(url,[],':eval');
    });

  jQuery(document).on("click", ".submit-reply", function(){ 
      url = jQuery(this).attr('data-url');
      parent_id = jQuery(this).attr('data-id');
      target = stringFormat('comment_replies_wrapper_{0}', parent_id)
      parent = stringFormat('parent_{0}', parent_id)
      reply_text = stringFormat('reply_text_{0}', parent_id)
      ajax(url, [parent, reply_text], target);
      jQuery(this).parent().remove()
      return false;
  }); 

  jQuery(document).on("click", ".cancel-reply", function(){
    jQuery(this).parent().remove()
    return false;
  });


  jQuery(document).on("click", ".remove-reply", function(){
    if (confirm("delete?")) {
        url = $(this).attr('data-url');
        ajax(url,[1],'');
        $(this).parent().hide();
    }
  });  

  $(".reply-button").click(function(){
    parent_id = $(this).parent().parent().parent().attr('data-cid');
    url = $(this).attr("data-url");
    obj = stringFormat("<div class='reply-form' id='reply-form-{0}'><input type='hidden' id='parent_{0}' name='parent_{0}' value='{0}'/><textarea id='reply_text_{0}' name='reply_text_{0}'></textarea><br/><button class='btn btn-primary submit-reply' data-id='{0}' data-url='{1}'>Ok</button> <button class='btn cancel-reply'>Cancel</button></div>", parent_id, url)
    $(this).parent().append(obj);
  });
   
});

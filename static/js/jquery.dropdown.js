jQuery(document).ready(function(){
   if(jQuery("ul.dropdown").length) {
       jQuery("ul.dropdown li").dropdown();
   }
});

jQuery.fn.dropdown = function() {
    return this.each(function() {
	    jQuery(this).hover(function(){
		    jQuery(this).addClass("hover");
		    jQuery('> .dir',this).addClass("open");
		    jQuery('ul:first',this).css('visibility', 'visible');
		},function(){
		    jQuery(this).removeClass("hover");
		    jQuery('.open',this).removeClass("open");
		    jQuery('ul:first',this).css('visibility', 'hidden');
		});
	});
}
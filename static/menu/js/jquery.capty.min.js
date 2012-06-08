/**
 * jQuery Capty - A Caption Plugin - http://wbotelhos.com/capty
 * 
 * @author	Washington Botelho
 * @twitter wbotelhos
 * @version 0.2.1
 * 
 * Licensed under The MIT License
 * http://opensource.org/licenses/mit-license.php
 * 
 */

(function(b){b.fn.capty=function(g){var k=b.extend({},b.fn.capty.defaults,g);if(this.length==0){a("Selector invalid or missing!");return;}else{if(this.length>1){return this.each(function(){b.fn.capty.apply(b(this),[g]);});}}var j=b(this),d=j.attr("name"),h=b('<div class="'+k.cCaption+'"/>'),e=j;if(j.parent().is("a")){e=j.parent();}var f=e.wrap('<div class="'+k.cImage+'"/>').parent(),i=f.wrap('<div class="'+k.cWrapper+'"/>').parent();i.css({height:j.height(),overflow:"hidden",position:"relative",width:j.width()});h.css({height:k.height,opacity:k.opacity,position:"relative"}).click(function(l){l.stopPropagation();}).appendTo(i);if(d){var c=b(d);if(c.length){c.appendTo(h);}else{h.html('<span style="color: #F00;">Content invalid or missing!</span>');}}else{h.html(j.attr("alt"));}if(k.prefix){h.prepend(k.prefix);}if(k.sufix){h.append(k.sufix);}if(k.animation=="slide"){i.hover(function(){h.animate({top:(-1*k.height)},{duration:k.speed,queue:false});},function(){h.animate({top:0},{duration:k.speed,queue:false});});}else{if(k.animation=="fade"){h.css({opacity:0,top:(-1*k.height)+"px"});i.hover(function(){h.stop().animate({opacity:k.opacity},k.speed);},function(){h.stop().animate({opacity:0},k.speed);});}else{if(k.animation=="fixed"){h.css("top",(-1*k.height)+"px");}else{a(j.attr("id")+": invalid animation!");}}}return j;};function a(c){if(window.console&&window.console.log){window.console.log(c);}}b.fn.capty.defaults={animation:"slide",cCaption:"capty-caption",cImage:"capty-image",cWrapper:"capty-wrapper",height:30,opacity:0.7,prefix:"",speed:200,sufix:""};})(jQuery);
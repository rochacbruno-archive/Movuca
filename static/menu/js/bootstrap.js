$(document).ready(function () {


  // $('.loader').ajaxStart(function(){
  //   $(this).show();
  // }).ajaxStop(function(){
  //   $(this).hide();
  // });
    

  // $("#loading_animation").bind({
  //     ajaxStart: function() { $(this).show(); },
  //     ajaxStop: function() { $(this).hide(); }
  // });
    
    //ajax($("#notification-dialog").attr("data-counter-url"),[],"notification-counter");

    $("#notification-dialog").dialog({
			autoOpen: false,
			show: "blind",
			hide: "explode"
	});
	$("#notification-dialog").bind( "dialogopen", function(event, ui) {
        ajax($("#notification-dialog").attr("data-url"),[],"notification-dialog");
    });
    $("#notification-dialog").bind( "dialogclose", function(event, ui) {
           $("#notification-dialog").empty();
           ajax($("#notification-dialog").attr("data-counter-url"),[],"notification-counter");
    });
    $("#notification-dialog").bind( "dialogbeforeclose", function(event, ui) {
           ajax($("#notification-dialog").attr("data-mark-url"),['notifications_ids'],"");
    });
	$( "#notification-opener" ).click(function() {
		obj = $("#notification-dialog");
		
		$("#notification-dialog").dialog( "option", "buttons", [
           
              {
               text: "Close and mark all as read",
               click: function() { $(this).dialog("close"); }
              }
               ] 
        );
        obj.dialog( "option", "height", 400 );
        obj.dialog( "option", "position", [$( "#notification-opener" ).offset().left,40] );
        //obj.dialog( "option", "title", 'Notifications' );
		$("#notification-dialog").dialog("open");
		return false;
	});


  // $(".delitem").click(function() {
  //     url = $(this).attr('data-url');
  //     if (confirm("Delete?")) {
  //       ajax(url,[],':eval');
  //       //jQuery($(this)).parent().hide();
  //       return false;
  //       }
  // });

});

// (function poll(){
//    setTimeout(function(){
//       ajax($("#notification-dialog").attr("data-counter-url"),[],"notification-counter");
//       poll();
//   }, 30000);
// })();
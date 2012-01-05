$(document).ready(function(){
$("#featured").tabs({fx:{opacity: "toggle"}}).tabs("rotate", 5000, true);
$("#featured").hover(
function() {
$("#featured").tabs("rotate",0,true);
},
function() {
$("#featured").tabs("rotate",5000,true);
}
);
});

// Binds page selector when DOM loads
$(document).ready(function(){
  $(".dropdown-item.training-type").click(function(e){
    $(".container.training_type").hide();
    $("#" + e.currentTarget.name).show();
    $("#screen_title").text(e.currentTarget.textContent);
  })
});
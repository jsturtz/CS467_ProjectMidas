$(document).ready(function(){

  // controls which page is displayed when user selects dropdown
  $(".dropdown-item.training-type").click(function(e){
    $(".container.training_type").hide();
    $("#" + e.currentTarget.name).show();
    $("#screen_title").text(e.currentTarget.textContent);
  })

  // checks whether input extension is valid
  $("#raw-data-input").change(function (e) {
    var fileExtension = ['csv'];
    if ($.inArray($(this).val().split('.').pop().toLowerCase(), fileExtension) == -1) {
        alert("Only formats allowed : " + fileExtension.join(', '));
        $("#raw-data-form")[0].reset();
    }
    else {
      // the e.currentTarget.value will hold path we need
      // pass this to backend business logic when we get that figured out
      console.log(e.currentTarget.value);
    }
  });
});


/* eslint-disable indent */
$(document).ready( () => {

  // controls which page is displayed when user selects dropdown
  $(".dropdown-item.training-type").click( e => {
    $(".container.training_type").hide();
    $("#" + e.currentTarget.name).show();
    $("#screen_title").text(e.currentTarget.textContent);
  })

  // import file from frontend
  $("#raw-data-form").on("submit", e => {
    $("#import_result").html("Uploading...");
    e.preventDefault();
    var data = new FormData($('#raw-data-form').get(0));

    $.ajax({
      url: window.location.pathname, 
      type: 'POST',
      data: data,
      processData: false,
      contentType: false,
      cache: false,
      success: res => {
        if (res.error)
        {
          $("#import_result").html("Error Uploading: " + res.message.filepath[0]);
        }
        else 
        {
          $("#import_result").html("File Successfully Uploaded");
        }
      }
    });
  });

  // clear message if user clicks on browse
  $("#id_filepath").on("click", e => {
    $("#import_result").html("");
    var data = new FormData($('#raw-data-form').get(0));
  });
});
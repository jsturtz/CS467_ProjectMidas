// only when document fully loaded
$(document).ready( () => {

  // event listeners on screen
  $(".dropdown-item.training-type").click(bindDropDown);
  $("#raw-data-form").on("submit", bindImportFile);
  $("#id_filepath").on("click", bindClearMessage);
  $("#generate-dict").on("click", bindDictGenerate);

  // settings for scrolls must be done in javascript
  $('.scrollboth').DataTable({
    "scrollX": true,
    "scrollY": 500,
  });
  $('.dataTables_length').addClass('bs-select');
});

// controls which page is displayed when user selects dropdown
function bindDropDown(e) 
{
  $(".container.training_type").hide();
  $("#" + e.currentTarget.name).show();
  $("#screen_title").text(e.currentTarget.textContent);
}

// import file from frontend
function bindImportFile(e) {
  $("#upload_result").html("Uploading...");
  e.preventDefault();
  var data = new FormData($('#raw-data-form').get(0));
  data.append("do", "upload");  // essential for telling postroute what to do

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
        $("#upload_result").html("Error Uploading: " + res.message.filepath[0]);
      }
      else 
      {
        $("#upload_successful").html("true");
        $("#upload_result").html("File Successfully Uploaded");
      }
    }
  });
}

// clear message if user clicks on browse
function bindClearMessage(e) {
  $("#upload_result").html("");
  var data = new FormData($('#raw-data-form').get(0));
}

  // clear message if user clicks on browse
function bindDictGenerate(e)
{
  e.preventDefault();
  if ($("#upload_successful").text() == "true")
  {
    var data = new FormData();
    data.append("do", "generate_dict");  // essential for telling postroute what to do

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
          console.log("Error!");
        }
        else 
        {
          console.log("Success!");
        }
      }
    });
  }
  else{
    console.log("Nothing yet imported");
  }
}
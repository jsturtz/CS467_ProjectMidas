// only when document fully loaded
$(document).ready( () => {
  console.log("home loaded");
  $(".upload-form").on("submit", bindImportFile);
  $(".dropdown-item.screen-type").click(toggleScreens);
})

// controls which page is displayed when user selects dropdown
function toggleScreens(e) 
{
  $("#screen-title").text(e.currentTarget.textContent);
  $(".container.screen-type").hide();
  $("#" + e.currentTarget.name).show();
}

// import file from frontend
function bindImportFile(e) {
  e.preventDefault();
  var thisform = $(this);
  var parent = $(thisform.parent());
  parent.find(".upload-result").html("Uploading...");

  // decide whether to upload training or testing file
  // required by post route for /train/
  var data = new FormData(thisform.get(0));
  data.append("action", "upload");

  if (parent.find("label").text().includes("Training")){
    data.append("file_type", "training");
  }
  else if (parent.find("label").text().includes("Testing")){
    data.append("file_type", "testing");  
  }
  else {
    throw "That aint it chief!";
  }

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
        parent.find(".upload-result").html("Error Uploading: " + res.message.filepath[0]);
      }
      else 
      {
        if (parent.find("label").text().includes("Training")){
          $("#section-data-prep").show()
        }
        parent.find(".upload-result").text("File Successfully Uploaded");
        parent.find(".upload-result").attr("success", "true");
      }
    }
  });
}

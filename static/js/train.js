// only when document fully loaded
$(document).ready( () => {

  // event listeners on screen
  $(".dropdown-item.training-type").click(bindDropDown);
  $("#id_filepath").on("click", bindClearMessage);
  $("#choose-dtypes").on("click", bindGetDataTypes);
  $(".upload-form").on("submit", bindImportFile);
  $("#data-cleaning-form").on("submit", bindCleaningForm);
  
  // $("#generate-dict").on("click", bindDictGenerate);

  // settings for scrolls must be done in javascript
  updateStylingDictionary();
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
  else if (parent.find("label").text().includes("Identity")){
    data.append("file_type", "upload_identity");  
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
        parent.find(".upload-result").text("File Successfully Uploaded");
        $("#dict_training").html(res)
        $(".feature_detail").on("click", bindFeatureDetails);
        updateStylingDictionary();
      }
    }
  });
}

// clear message if user clicks on browse
function bindClearMessage(e) {
  $("#upload_result").html("");
  var data = new FormData($('#raw-data-form').get(0));
}

function updateStylingDictionary() {

  $('.scrollboth').DataTable({
    "scrollX": true,
    "scrollY": 500,
  });
  $('.dataTables_length').addClass('bs-select');

}

function bindFeatureDetails(e) {
  e.preventDefault();
  feature = $(this).text() 
  $.ajax({
    type: 'GET', 
    url: "/train?feature_detail=" + feature, 
    success: res => {
      $('#feature-header').text("Analysis of Feature " + feature)
      $('#feature-body').html(res)
      $('#feature-modal').modal()
    },
    error: res => {
      alert(res.message)
    }
  });
}

// import file from frontend
function bindCleaningForm(e) {
  e.preventDefault();
  var thisform = $(this);
  var data = new FormData(thisform.get(0));
  data.append("action", "cleaning");

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
        $('#dtype-selection-result').text("Error submitting...");
      }
      else 
      {
        $('#dtype-selection-result').text("Successfully submitted data cleaning options");
      }
    }
  });
}

function bindGetDataTypes(e) {
  e.preventDefault();
  $.ajax({
    type: 'GET', 
    url: "/train?recommended_dtypes=true", 
    success: res => {
      $('#dtype-selection-body').html(res)
      $('#dtype-selection-modal').modal()
    },
    error: res => {
      alert(res.message)
    }
  });
}


// only when document fully loaded
$(document).ready( () => {

  // event listeners on screen
  $(".dropdown-item.training-type").click(bindDropDown);
  $("#id_filepath").on("click", bindClearMessage);
  $("#choose-dtypes").on("click", bindGetDataTypes);
  $(".upload-form").on("submit", bindImportFile);
  $("#data-cleaning-form").on("submit", bindCleaningForm);
  $("#id_do_imputation").on("change", bindToggleImputation);
  $("#id_do_PCA").on("change", bindTogglePCA);
  $("#submit-data-dict").on("click", bindConfirmFeatures);
  $("#choose-outcome").on("click", bindGetColumns);
  $("#submit-outcome").on("click", submitOutcome);

  // initializations when page is loaded
  updateStylingDictionary();
  $("#div_id_numeric_strategy").hide()
  $("#div_id_categorical_strategy").hide()
  $("#div_id_variance_retained").hide()
  $("#id_do_imputation").prop('checked', false)
  $("#id_do_PCA").prop('checked', false)
})

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

        $("#section-data-prep").show()
        parent.find(".upload-result").text("File Successfully Uploaded");
      }
    }
  });
}

function bindGetColumns(e) {
  e.preventDefault();
  feature = $(this).text() 
  $.ajax({
    type: 'GET', 
    url: "/?columns=True", 
    success: res => {
      $('#outcome-selection-body').html(res)
      $('#outcome-selection-modal').modal()
    },
    error: res => {
      alert(res.message)
    }
  });
}

// import file from frontend
function submitOutcome(e) {
  e.preventDefault();
  // var thisform = $("#select-outcome-form");
  // var data = new FormData(thisform.get(0));
  var data = {"outcome": $(".outcome-radio:checked").val(), "action": "outcome"};
  console.log(data);

  $.ajax({
    url: window.location.pathname, 
    type: 'POST',
    data: data,
    cache: false,
    success: res => {
      if (res.error)
      {
        console.log("Hello error!");
        $('#outcome-selection-result').text(res.message);
      }
      else 
      {
        console.log("Hello success!");
        $("#section-choose-dtypes").show()
        $('#outcome-selection-result').text("Successfully chose response variabel");
      }
    }
  });
}


function bindConfirmFeatures(e) 
{
  var thisform = $("#select-data-types-form");
  var data = new FormData(thisform.get(0));
  console.log(data);
  data.append("action", "analysis");

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
        alert("Uh oh!")
        parent.find(".upload-result").html("Error Making Data Dictionary: " + res.message.filepath[0]);
      }
      else 
      {
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
    url: "/?feature_detail=" + feature, 
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
        console.log("Hello error!");
        $('#dtype-selection-result').text(res.message);
      }
      else 
      {
        console.log("Hello success!");
        $('#dtype-selection-result').text("Successfully submitted data cleaning options");
      }
    }
  });
}


function bindGetDataTypes(e) {
  e.preventDefault();
  $.ajax({
    type: 'GET', 
    url: "/?recommended_dtypes=true", 
    success: res => {
      $('#dtype-selection-body').html(res)
      $('#dtype-selection-modal').modal()
    },
    error: res => {
      alert(res.message)
    }
  });
}

function bindToggleImputation(e) {
  e.preventDefault();
  $("#div_id_numeric_strategy").toggle()
  $("#div_id_categorical_strategy").toggle()
}

function bindTogglePCA(e) {
  e.preventDefault();
  $("#div_id_variance_retained").toggle()
}

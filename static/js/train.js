// only when document fully loaded
$(document).ready( () => {
  refreshBindings();
})

function refreshBindings()
{

  // event listeners on screen
  $("#id_filepath").on("click", bindClearMessage);
  $("#choose-dtypes").on("click", bindGetDataTypes);
  $(".upload-form").on("submit", bindImportFile);
  $("#data-cleaning-form").on("submit", bindCleaningForm);
  $("#id_do_imputation").on("change", bindToggleImputation);
  $("#id_do_PCA").on("change", bindTogglePCA);
  $("#submit-data-dict").on("click", bindConfirmFeatures);
  $("#choose-outcome").on("click", bindGetColumns);
  $("#submit-outcome").on("click", submitOutcome);
  $(".dropdown-item.ml-algorithm").on("click", chooseAlgorithm);

  // initializations when page is loaded
  $("#div_id_numeric_strategy").hide()
  $("#div_id_categorical_strategy").hide()
  $("#div_id_variance_retained").hide()
  $("#div_id_do_PCA").hide()
  $("#id_do_imputation").prop('checked', false)
  $("#id_do_PCA").prop('checked', false)
}

function bindGetColumns(e) {
  console.log("THis was hit");
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

function submitOutcome(e) {
  e.preventDefault();
  // var thisform = $("#select-outcome-form");
  // var data = new FormData(thisform.get(0));
  var data = {"outcome": $(".outcome-radio:checked").val(), "action": "outcome"};
  var result = $("#section-data-prep").find(".result").first();
  result.text("Submitting response variable...");

  $.ajax({
    url: window.location.pathname, 
    type: 'POST',
    data: data,
    cache: false,
    success: res => {
      if (res.error)
      {
        result.text("Failed to submit response variable");
        $('#outcome-selection-result').text(res.message);
      }
      else 
      {
        result.text("Response Variable: " + res.outcome);
        $("#section-choose-dtypes").show()
        $('#outcome-selection-result').text("Successfully chose response variable");
      }
    }
  });
}


function bindConfirmFeatures(e) 
{
  var thisform = $("#select-data-types-form");
  var data = new FormData(thisform.get(0));
  data.append("action", "analysis");
  var result = $("#section-choose-dtypes").find(".result").first();
  result.text("Updating data types...");
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
        parent.find(".upload-result").html("Error Making Data Dictionary: " + res.message.filepath[0]);
      }
      else 
      {
        result.text("Data Types Updated");
        $("#dict_training").html(res);
        $("#section-analysis").show();
        $("#section-choose-model").show();
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

// FIXME: Make sure to stop this from moving the cursor up to teh top of the page. Annoying
function chooseAlgorithm(e) {
  console.log("This code is hit");
  $.ajax({
    type: 'GET', 
    url: "/?cleaning_options=" + e.currentTarget.name, 
    success: res => {
      $("#select_model").text(e.currentTarget.textContent);
      $("#cleaning-form").html(res);
      $("#section-cleaning").show();
      refreshBindings();
    },
    error: res => {
      alert(res.message);
    }
  });

}

function bindCleaningForm(e) {

  e.preventDefault();
  $('#data-cleaning-form').find(".result").text("Submitting options and training...(this may take some time)");
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


// <form id="data-cleaning-form" method="POST" enctype="multipart/form-data" data-ajax="false">
//     {% csrf_token %}
//     {{ form|crispy }}
//   <input type="submit" value="Submit and Train Model">
//   <div class="result"></div>
// </form>
      //
      if (res.error)
      {
        $('#data-cleaning-form').find(".result").text("Error training data, try again");
      }
      else 
      {
        $('#data-cleaning-form').find(".result").text("Successfully trained model!");
        $("#section-train-results").find(".results").html(res);
        $("#section-train-results").show()
        $("#save-model-form").on("submit", saveModel);


// <form id="save-model-form">
//   <div class="form-group">
//     <label for="name-model">Name Your Model</label>
//     <textarea class="form-control" id="name-model" rows="3"></textarea>
//   </div>
// </form>
      }
    }
  });
}

function saveModel(e)
{
  console.log("saveModel called");
  e.preventDefault();
  var pretty_name = $("#model-name").val();
  console.log("pretty_name: " + pretty_name);
  // var data = {action: "save", pretty_name: pretty_name};
  var data = new FormData();
  data.append("action", "save");
  data.append("pretty_name", pretty_name);     

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
        alert("Failed to save model!");
      }
      else 
      {
        alert("Model saved!");
        location.reload();
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
  if ($(this).prop("checked"))
  {
    $("#div_id_numeric_strategy").show();
    $("#div_id_categorical_strategy").show();
    $("#div_id_do_PCA").show();
    $("#div_id_variance_retained").hide();
    $("#id_do_PCA").prop('checked', false);
  }
  else 
  {
    $("#div_id_numeric_strategy").hide();
    $("#div_id_categorical_strategy").hide();
    $("#div_id_do_PCA").hide();
    $("#div_id_variance_retained").hide();
    $("#id_do_PCA").prop('checked', false);
  }
}

function bindTogglePCA(e) {
  e.preventDefault();
  $("#div_id_variance_retained").toggle();
}

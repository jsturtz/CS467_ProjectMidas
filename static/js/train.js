// only when document fully loaded
$(document).ready( () => {

  // event listeners on screen
  $(".dropdown-item.training-type").click(bindDropDown);
  $(".upload-form").on("submit", bindImportFile);

  $("#id_filepath").on("click", bindClearMessage);
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

  // decide whether to upload transction or identity file
  // required by post route for /train/
  var data = new FormData(thisform.get(0));
  var dict_element;
  if (parent.find("label").text().includes("Transaction")){
    data.append("do", "upload_transaction");
    dict_element = "#dict_transaction";
  }
  else if (parent.find("label").text().includes("Identity")){
    data.append("do", "upload_identity");  
    dict_element = "#dict_identity";
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
        $(dict_element).html(res.data)
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
  // clear message if user clicks on browse
// function bindDictGenerate(e)
// {
//   e.preventDefault();
//   var data = new FormData();
//   data.append("do", "generate_dict");  // essential for telling postroute what to do

//   $.ajax({
//     url: window.location.pathname, 
//     type: 'POST',
//     data: data,
//     processData: false,
//     contentType: false,
//     cache: false,
//     success: res => {
//       if (res.error)
//       {
//         console.log("Error!");
//       }
//       else 
//       {
//         console.log(res.message)
//       }
//     }
//   });
// }